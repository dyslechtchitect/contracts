const AWS  = require('aws-sdk');
const ddb = new AWS.DynamoDB.DocumentClient();

exports.handler = async (event, context) => {
    try {
        if (!event.requestContext.authorizer) {
            return errorResponse('Authorization not configured', context.awsRequestId);
        }

        
        const requestBody = JSON.parse(event.body);
        const ownerUserId = event.requestContext.authorizer.claims['sub'];
        const sharedWithUserId = requestBody.sharedWithUserId;
        const contractId = requestBody.contractId;
        console.log(`xxx ${ownerUserId}, ${sharedWithUserId}` )

        if (ownerUserId == sharedWithUserId) {
            return errorResponse('you cannot share a contract with yourself duh', context.awsRequestId);
        };

        const contract = await fetchContracts(ownerUserId, contractId)

        if (!!contract) {
            return errorResponse('contract does not exist', context.awsRequestId);
        };

        if (!contract?.isCreator) {
            return errorResponse('you cannot share a contract unless you own it', context.awsRequestId);
        };

        await shareContract(sharedWithUserId, contractId);

        return {
            statusCode: 201,
            body: JSON.stringify({
                contractId: contractId,
                sharedWithUserId: sharedWithUserId,
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

async function fetchContracts(userId, contractId) {
    return ddb.get({
        TableName: 'contracts',
        Key: {
            id: contractId,
            userId: userId
        },
    }).promise();
};

async function shareContract(sharedWithUserId, contractId) {
    const contractsToUsersItem = {
        TableName: 'contracts_to_users',
        Item: {
            contractId: contractId,
            userId: sharedWithUserId,
            isCreator: false,
            isEditor: false,
            isParty: true
        }
    }
   
    await ddb.put(contractsToUsersItem).promise();
}

function errorResponse(errorMessage, awsRequestId) {
    return {
        statusCode: 403,
        body: JSON.stringify({
            Error: errorMessage,
            Reference: awsRequestId,
        }),
        headers: {
            'Access-Control-Allow-Origin': '*',
        },
    };
}
