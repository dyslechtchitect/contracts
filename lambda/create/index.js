const { randomUUID } = require('crypto');
const AWS  = require('aws-sdk');
const ddb = new AWS.DynamoDB.DocumentClient();

exports.handler = async (event, context) => {
    try {
        if (!event.requestContext.authorizer) {
            return errorResponse('Authorization not configured', context.awsRequestId);
        }

        const userId = event.requestContext.authorizer.claims['sub'];
        const contractId = randomUUID();

        console.log('Received context', context);
        console.log('Received event', event);
        console.log('Received contractId', contractId);
        console.log('Received userId', userId);

        const username = event.requestContext.authorizer.claims['cognito:username'];
        const requestBody = JSON.parse(event.body);

        await createContract(userId, contractId, username, requestBody);

        return {
            statusCode: 201,
            body: JSON.stringify({
                ContractId: contractId,
                Contract: requestBody,
                userId: userId,
                username: username,
                createdDate: new Date().toISOString(),
                updatedDate: new Date().toISOString(),
            }),
            headers: {
                'Access-Control-Allow-Origin': '*',
            },
        };
    } catch (error) {
        console.error(error);
        return errorResponse(error.message, context.awsRequestId);
    }
};

async function createContract(userId, contractId, username, body) {
    const contractItem = {
        TableName: 'contracts',
        Item: {
            id: contractId,
            userId: userId,
            username: username,
            body: body,
            createdDate: new Date().toISOString(),
            updatedDate: new Date().toISOString(),
        },
    }

    const contractsToUsersItem = {
        TableName: 'contracts_to_users',
        Item: {
            contractId: contractId,
            userId: userId,
            isCreator: true,
            isEditor: true,
            isParty: false
        },
    }

    const transactionItems = {
        TransactItems: [
            {
                Put: contractItem
            },
            {
                Put: contractsToUsersItem
            }
        ]
    };

    await ddb.transactWrite(transactionItems).promise();
}

function errorResponse(errorMessage, awsRequestId) {
    return {
        statusCode: 500,
        body: JSON.stringify({
            Error: errorMessage,
            Reference: awsRequestId,
        }),
        headers: {
            'Access-Control-Allow-Origin': '*',
        },
    };
}
