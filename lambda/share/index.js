const { randomUUID } = require('crypto');
const AWS  = require('aws-sdk');
const ddb = new AWS.DynamoDB.DocumentClient();

exports.handler = async (event, context) => {
    try {
        if (!event.requestContext.authorizer) {
            return errorResponse('Authorization not configured', context.awsRequestId);
        }

        

        const userId = event.requestContext.authorizer.claims['sub'];
        const contractId = event.queryStringParameters?.contractId ?? event.pathParameters?.contractId;
        
        if (userid == contractId) {
            return errorResponse('you cannot share a contract with yourself duh', context.awsRequestId);
        }

        console.log('Received context', context);
        console.log('Received event', event);
        console.log('Received contractId', contractId);
        console.log('Received userId', userId);

        const username = event.requestContext.authorizer.claims['cognito:username'];
        const requestBody = JSON.parse(event.body);

        await shareContract(userId, contractId);

        return {
            statusCode: 201,
            body: JSON.stringify({
                contractId: contractId,
                userId: userId,
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

async function shareContract(userId, contractId) {
    const share = {
        TableName: 'contracts_to_users',
        Item: {
            'id': contractId,
            'userId': userId,
            'isCreator': false,
            'isEditor': false,
            'isParty': true
        },
        ConditionExpression: 'attribute_exists(id)'
    }

    await ddb.put(share).promise();
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
