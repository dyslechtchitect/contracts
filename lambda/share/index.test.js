const AWSMOCK = require("aws-sdk");

const { handler } = require('./index.js');
const { randomUUID } = require("crypto");


let mockDocumentClient = {
  put: {
    promise: jest.fn()
  },
};

jest.mock("aws-sdk", () => {
  return {
    DynamoDB: {
      DocumentClient: jest.fn().mockImplementation(() => {
        return {
          put: () => mockDocumentClient.put,
        };
      }),
    },
  };
});

test('fail when a user shares a contract with themselves', async () => {
  const userId = randomUUID();
  const body = {
    sharedWithUserId: userId,
    contractId: randomUUID()
  }
  const event = {
    path: '/contract',
    httpMethod: 'POST',
    headers: {
      Accept: '*/*',
      Authorization: 'eyJraWQiOiJLTzRVMWZs',
      'content-type': 'application/json; charset=UTF-8',
    },
    queryStringParameters: null,
    pathParameters: null,
    requestContext: {
      authorizer: {
        claims: {
          'cognito:username': 'the_username',
          sub: userId,
        },
      },
    },
    body: JSON.stringify(body),
  };

  const context = { awsRequestId: 'awsRequestId' };

  // Invoke the handler
  const result = await handler(event, context);

  // Assertions
  expect(result.statusCode).toBe(403);
 
});
