// src/config/cognitoAuthConfig.js

const cognitoAuthConfig = {
    authority: "https://us-east-1rqshizp2h.auth.us-east-1.amazoncognito.com",
    client_id: "4pca6q1su26h9unk3qqeg2o6f7",
    redirect_uri: "http://localhost:3000",
    response_type: "code",
    scope: "openid profile email",
};

export default cognitoAuthConfig;