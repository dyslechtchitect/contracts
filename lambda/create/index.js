const { randomUUID } = require('crypto');
const AWS = require('aws-sdk');
const ddb = new AWS.DynamoDB.DocumentClient();

exports.handler = (event, context, callback) => {

    if (!event.requestContext.authorizer) {
      errorResponse('Authorization not configured', context.awsRequestId, callback);
      return;
    }
    
    const userId = event.requestContext.authorizer.claims['sub'];
    const contractId = randomUUID();

    console.log('Received context', context);
    console.log('Received event', event);
    console.log('Received contractId', contractId);
    console.log('Received userId', userId);

    const username = event.requestContext.authorizer.claims['cognito:username'];
    const requestBody = JSON.parse(event.body);


    createContract(userId, contractId, username, requestBody).then(() => {
        callback(null, {
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
        });
    }).catch((err) => {
        console.error(err);
        errorResponse(err.message, context.awsRequestId, callback)
    });
};


function createContract(userId, contractId, username, contract) {
    return ddb.put({
        TableName: 'contracts',
        Item: {
            userId: userId,
            contractId: contractId,
            username: username,
            Contract: contract,
            createdDate: new Date().toISOString(),
        },
    }).promise();
}

function errorResponse(errorMessage, awsRequestId, callback) {
  callback(null, {
    statusCode: 500,
    body: JSON.stringify({
      Error: errorMessage,
      Reference: awsRequestId,
    }),
    headers: {
      'Access-Control-Allow-Origin': '*',
    },
  });
}