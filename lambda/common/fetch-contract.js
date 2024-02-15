export function fetchContract(userId, contractId) {
    return ddb.get({
        TableName: 'contracts',
        Key: {
            id: contractId,
            userId: userId
        },
    }).promise();
}