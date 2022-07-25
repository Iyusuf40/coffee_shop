/* @TODO replace with your variables
 * ensure all variables on this page match your project
 */

export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: "yusuf-fsnd-udacity.us", // the auth0 domain prefix
    audience: 'drinks', // the audience set for the auth0 app
    clientId: 'T2O0rnDZGFxiMSEvApEWmOl8OLp7gwXJ', // the client id generated for the auth0 app
    callbackURL: "http://localhost:3000/tabs/drink-menu", // the base url of the running ionic application. 
  }
};
