const AWS = require('aws-sdk');
const ddb = new AWS.DynamoDB.DocumentClient();
const foo = require('../test.js').foo;
exports.handler = (event, context, callback) => {
    foo(); // this may not work
    if (!event.requestContext.authorizer) {
      errorResponse('Authorization not configured', context.awsRequestId, callback);
      return;
    };

    
    const userId = event.requestContext.authorizer.claims?.sub;
    const contractId = event.queryStringParameters?.contractId ?? event.pathParameters?.contractId ;
    

    console.log('Received contractId', contractId);
    console.log('Received userId', userId);
    if (!!contractId) {
    fetchContract(userId, contractId).then((result, error) => {
        callback(null, {
            statusCode: 200,
            body: JSON.stringify(
                [result.Item]
            ),
            headers: {
                'Access-Control-Allow-Origin': '*',
            },
        });
    }).catch((err) => {
        console.error(err);

        errorResponse(err, context.awsRequestId, callback)
    });
    } else {
        listUnicorns(userId).then((result, error) => {
              console.log('Received result', result);
        callback(null, {
            statusCode: 200,
            body: JSON.stringify(
                result
            ),
            headers: {
                'Access-Control-Allow-Origin': '*',
            },
        });
    }).catch((err) => {
        console.error(err);

        errorResponse(err.message, context.awsRequestId, callback)
    });
    }
};

function fetchContract(userId, contractId) {
    return ddb.get({
        TableName: 'contracts',
        Key: {
            id: contractId,
            userId: userId
        },
    }).promise();
};

function listUnicorns(userId) {

const params = {
    TableName: 'contracts_to_users',
    IndexName: 'userId-contractId-index', 
    KeyConditionExpression: 'userId = :userId',
    ExpressionAttributeValues: {
        ':userId': userId
    }
};
    const contracts = ddb.query(params)
    console.log(contracts.toString)
  
    return contracts.promise();
};


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