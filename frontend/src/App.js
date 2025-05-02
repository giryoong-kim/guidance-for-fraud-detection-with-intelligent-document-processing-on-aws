import React, { useEffect, useRef, useState } from "react";
import { HashRouter, BrowserRouter, Routes, Route } from "react-router-dom";
import { 
  REGION,
  USE_BROWSER_ROUTER,
  COGNITO_USER_POOL_ID,
  COGNITO_USER_POOL_CLIENT_ID
 } from "./common/constants";
import GlobalHeader from "./components/global-header";
import HomePage from "./pages/home";
import Create from "./pages/workflow/create/create-page";
import Review from "./pages/workflow/review/review-page";
import ReviewDetail from "./pages/workflow/review/review-detail-page";
import { Amplify, Auth } from "aws-amplify";
import "@aws-amplify/ui-react/styles.css";
import { Authenticator } from "@aws-amplify/ui-react";
import {
  Link,
} from "@cloudscape-design/components";

//import "./styles/app.scss";
import NotFound from "./pages/not-found";

Auth.configure({
  aws_project_region: REGION,
  aws_cognito_region: REGION,
  aws_user_pools_id: COGNITO_USER_POOL_ID,
  aws_user_pools_web_client_id: COGNITO_USER_POOL_CLIENT_ID,
  oauth: {},
  aws_cognito_signup_attributes: ["EMAIL"],
  aws_cognito_username_attributes: ["EMAIL"],
  aws_cognito_password_protection_settings: {
    passwordPolicyMinLength: 8,
    passwordPolicyCharacters: [],
  },
  aws_cognito_verification_mechanisms: ["EMAIL"],
});

const user = await Amplify.Auth.currentAuthenticatedUser();
const token = user.signInUserSession.idToken.jwtToken;

export default function App() {
  const Router = USE_BROWSER_ROUTER ? BrowserRouter : HashRouter;

  return (
    <div style={{ height: "100%" }}>
      <Authenticator
      initialState="signIn"
      components={{
        SignUp: {
          FormFields() {
            return (
              <>
                <Authenticator.SignUp.FormFields />
                <div>
                  <label>Email</label><br/>
                  <input
                    type="email"
                    name="email"
                    placeholder="Enter your email"
                  />
                </div>
              </>
            );
          },
        },
      }}
    >
        {({ signOut, user }) => (
          <Router>
            <GlobalHeader/>
            <div style={{ height: "56px", backgroundColor: "#000716" }}>&nbsp;</div>
            <div>
              <Routes>
                <Route index path="/" element={<HomePage />} />
                <Route index path="/workflow/create" element={<Create token={token}/>} />
                <Route index path="/workflow/review" element={<Review token={token}/>} />
                <Route path = "/workflow/review/:claimId" element={<ReviewDetail token={token}/>}/>
                <Route path="*" element={<NotFound />} />
              </Routes>
            </div>
          </Router>
        )}
      </Authenticator>
    </div>
  );
}