// Ensure you have these dependencies installed in your package.json:
// "dependencies": {
//   "aws-sdk": "^2.1000.0",
//   "crypto": "^1.0.0",
//   "aws-sdk": "^2.1000.0"
// }

const { randomUUID } = require('crypto');
const AWS = require('aws-sdk');
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
                Eta: '30 seconds',
                Rider: username,
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

async function createContract(userId, contractId, username, contract) {
    console.log('Received ddb', ddb);
    await ddb.put({
        TableName: 'contract',
        Item: {
            userId: userId,
            contractId: contractId,
            username: username,
            Contract: contract,
            createdDate: new Date().toISOString(),
        },
    }).promise();
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
