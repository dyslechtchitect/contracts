import AWSMOCK from "aws-sdk";

import { handler } from './index.mjs';


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

test('should create contract in db returning 201 status code ', async () => {
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
          sub: 'the_user_id',
        },
      },
    },
    body: JSON.stringify({ foo: 'bar' }),
  };

  const context = { awsRequestId: 'awsRequestId' };

  // Invoke the handler
  const result = await handler(event, context);

  // Assertions
  expect(result.statusCode).toBe(201);
  expect(JSON.parse(result.body)).toEqual({
    ContractId: expect.any(String), // ContractId is generated randomly
    Contract: { foo: 'bar' },
    Eta: '30 seconds',
    Rider: 'the_username',
  });
});
