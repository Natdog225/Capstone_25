// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from 'firebase/auth';

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyBBMyD2Hb_H6rlEuZUzC68AN_lcXBq3d-I",
  authDomain: "dinemetra-01.firebaseapp.com",
  projectId: "dinemetra-01",
  storageBucket: "dinemetra-01.firebasestorage.app",
  messagingSenderId: "323674741624",
  appId: "1:323674741624:web:706c82bc1bc441c7ab068d"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();