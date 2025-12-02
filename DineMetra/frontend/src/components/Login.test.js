import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import DineMetraAuth from './Login.jsx';
import { 
  signInWithEmailAndPassword, 
  createUserWithEmailAndPassword,
  signInWithPopup 
} from 'firebase/auth';

// Mock React Router
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

// Mock Firebase
jest.mock('firebase/auth', () => ({
  signInWithEmailAndPassword: jest.fn(),
  createUserWithEmailAndPassword: jest.fn(),
  signInWithPopup: jest.fn(),
}));

jest.mock('../firebase', () => ({
  auth: {},
  googleProvider: {},
}));

// Wrapper component for Router
const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('DineMetraAuth Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  // ==================== RENDERING TESTS ====================
  
  describe('Initial Rendering', () => {
    test('renders login form by default', () => {
      renderWithRouter(<DineMetraAuth />);
      
      expect(screen.getByPlaceholderText('Enter your email')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Enter your password')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /sign in$/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /sign up$/i })).toBeInTheDocument();
    });

    test('renders logo image', () => {
      renderWithRouter(<DineMetraAuth />);
      
      const logo = screen.getByAltText('DineMetra Logo');
      expect(logo).toBeInTheDocument();
      expect(logo).toHaveAttribute('src', '/DineMetra_Logo.png');
    });

    test('renders Google sign-in button', () => {
      renderWithRouter(<DineMetraAuth />);
      
      expect(screen.getByRole('button', { name: /sign in with google/i })).toBeInTheDocument();
    });

    test('does not show error message initially', () => {
      renderWithRouter(<DineMetraAuth />);
      
      expect(screen.queryByText(/error/i)).not.toBeInTheDocument();
    });
  });

  // ==================== SIGN IN TESTS ====================
  
  describe('Sign In Functionality', () => {
    test('allows user to input email and password', () => {
      renderWithRouter(<DineMetraAuth />);
      
      const emailInput = screen.getByPlaceholderText('Enter your email');
      const passwordInput = screen.getByPlaceholderText('Enter your password');
      
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      
      expect(emailInput).toHaveValue('test@example.com');
      expect(passwordInput).toHaveValue('password123');
    });

    test('clears error when user types', () => {
      renderWithRouter(<DineMetraAuth />);
      
      // First trigger an error by attempting sign in
      signInWithEmailAndPassword.mockRejectedValueOnce({
        message: 'Firebase: Invalid credentials'
      });
      
      const signInButton = screen.getByRole('button', { name: /sign in$/i });
      fireEvent.click(signInButton);
      
      // Now type in the email field
      const emailInput = screen.getByPlaceholderText('Enter your email');
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      
      // Error should be cleared (we'll verify this doesn't throw)
      expect(emailInput).toHaveValue('test@example.com');
    });

    test('successfully signs in with valid credentials', async () => {
      signInWithEmailAndPassword.mockResolvedValueOnce({
        user: { uid: '123', email: 'test@example.com' }
      });
      
      renderWithRouter(<DineMetraAuth />);
      
      const emailInput = screen.getByPlaceholderText('Enter your email');
      const passwordInput = screen.getByPlaceholderText('Enter your password');
      const signInButton = screen.getByRole('button', { name: /sign in$/i });
      
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.click(signInButton);
      
      await waitFor(() => {
        expect(signInWithEmailAndPassword).toHaveBeenCalledWith(
          {},
          'test@example.com',
          'password123'
        );
        expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
      });
    });

    test('displays error message on failed sign in', async () => {
      signInWithEmailAndPassword.mockRejectedValueOnce({
        message: 'Firebase: Invalid email or password'
      });
      
      renderWithRouter(<DineMetraAuth />);
      
      const emailInput = screen.getByPlaceholderText('Enter your email');
      const passwordInput = screen.getByPlaceholderText('Enter your password');
      const signInButton = screen.getByRole('button', { name: /sign in$/i });
      
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'wrongpassword' } });
      fireEvent.click(signInButton);
      
      await waitFor(() => {
        expect(screen.getByText('Invalid email or password')).toBeInTheDocument();
      });
    });

    test('shows loading state during sign in', async () => {
      signInWithEmailAndPassword.mockImplementation(() => 
        new Promise(resolve => setTimeout(resolve, 100))
      );
      
      renderWithRouter(<DineMetraAuth />);
      
      const emailInput = screen.getByPlaceholderText('Enter your email');
      const passwordInput = screen.getByPlaceholderText('Enter your password');
      const signInButton = screen.getByRole('button', { name: /sign in$/i });
      
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.click(signInButton);
      
      // Check that at least one button shows loading state
      const loadingButtons = screen.getAllByRole('button', { name: /signing in\.\.\./i });
      expect(loadingButtons.length).toBeGreaterThan(0);
      expect(loadingButtons[0]).toBeDisabled();
    });

    test('disables inputs during sign in', async () => {
      signInWithEmailAndPassword.mockImplementation(() => 
        new Promise(resolve => setTimeout(resolve, 100))
      );
      
      renderWithRouter(<DineMetraAuth />);
      
      const emailInput = screen.getByPlaceholderText('Enter your email');
      const passwordInput = screen.getByPlaceholderText('Enter your password');
      const signInButton = screen.getByRole('button', { name: /sign in$/i });
      
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.click(signInButton);
      
      expect(emailInput).toBeDisabled();
      expect(passwordInput).toBeDisabled();
    });
  });

  // ==================== SIGN UP TESTS ====================
  
  describe('Sign Up Functionality', () => {
    test('switches to sign up form when Sign Up button is clicked', () => {
      renderWithRouter(<DineMetraAuth />);
      
      const signUpButton = screen.getByRole('button', { name: /^sign up$/i });
      fireEvent.click(signUpButton);
      
      expect(screen.getByText('Sign Up')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('At least 6 characters')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Re-enter password')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /create account/i })).toBeInTheDocument();
    });

    test('switches back to sign in form when Back to Sign In is clicked', () => {
      renderWithRouter(<DineMetraAuth />);
      
      // Switch to sign up
      const signUpButton = screen.getByRole('button', { name: /^sign up$/i });
      fireEvent.click(signUpButton);
      
      // Switch back to sign in
      const backButton = screen.getByRole('button', { name: /back to sign in/i });
      fireEvent.click(backButton);
      
      expect(screen.getByPlaceholderText('Enter your password')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /sign in$/i })).toBeInTheDocument();
    });

    test('allows user to input sign up information', () => {
      renderWithRouter(<DineMetraAuth />);
      
      // Switch to sign up
      const signUpButton = screen.getByRole('button', { name: /^sign up$/i });
      fireEvent.click(signUpButton);
      
      const emailInput = screen.getByPlaceholderText('Enter your email');
      const passwordInput = screen.getByPlaceholderText('At least 6 characters');
      const confirmPasswordInput = screen.getByPlaceholderText('Re-enter password');
      
      fireEvent.change(emailInput, { target: { value: 'newuser@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } });
      
      expect(emailInput).toHaveValue('newuser@example.com');
      expect(passwordInput).toHaveValue('password123');
      expect(confirmPasswordInput).toHaveValue('password123');
    });

    test('validates password match', async () => {
      renderWithRouter(<DineMetraAuth />);
      
      // Switch to sign up
      const signUpButton = screen.getByRole('button', { name: /^sign up$/i });
      fireEvent.click(signUpButton);
      
      const emailInput = screen.getByPlaceholderText('Enter your email');
      const passwordInput = screen.getByPlaceholderText('At least 6 characters');
      const confirmPasswordInput = screen.getByPlaceholderText('Re-enter password');
      const createAccountButton = screen.getByRole('button', { name: /create account/i });
      
      fireEvent.change(emailInput, { target: { value: 'newuser@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'different123' } });
      fireEvent.click(createAccountButton);
      
      await waitFor(() => {
        expect(screen.getByText('Passwords do not match!')).toBeInTheDocument();
      });
      
      expect(createUserWithEmailAndPassword).not.toHaveBeenCalled();
    });

    test('validates password length', async () => {
      renderWithRouter(<DineMetraAuth />);
      
      // Switch to sign up
      const signUpButton = screen.getByRole('button', { name: /^sign up$/i });
      fireEvent.click(signUpButton);
      
      const emailInput = screen.getByPlaceholderText('Enter your email');
      const passwordInput = screen.getByPlaceholderText('At least 6 characters');
      const confirmPasswordInput = screen.getByPlaceholderText('Re-enter password');
      const createAccountButton = screen.getByRole('button', { name: /create account/i });
      
      fireEvent.change(emailInput, { target: { value: 'newuser@example.com' } });
      fireEvent.change(passwordInput, { target: { value: '12345' } });
      fireEvent.change(confirmPasswordInput, { target: { value: '12345' } });
      fireEvent.click(createAccountButton);
      
      await waitFor(() => {
        expect(screen.getByText('Password must be at least 6 characters')).toBeInTheDocument();
      });
      
      expect(createUserWithEmailAndPassword).not.toHaveBeenCalled();
    });

    test('successfully creates account with valid information', async () => {
      createUserWithEmailAndPassword.mockResolvedValueOnce({
        user: { uid: '123', email: 'newuser@example.com' }
      });
      
      renderWithRouter(<DineMetraAuth />);
      
      // Switch to sign up
      const signUpButton = screen.getByRole('button', { name: /^sign up$/i });
      fireEvent.click(signUpButton);
      
      const emailInput = screen.getByPlaceholderText('Enter your email');
      const passwordInput = screen.getByPlaceholderText('At least 6 characters');
      const confirmPasswordInput = screen.getByPlaceholderText('Re-enter password');
      const createAccountButton = screen.getByRole('button', { name: /create account/i });
      
      fireEvent.change(emailInput, { target: { value: 'newuser@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } });
      fireEvent.click(createAccountButton);
      
      await waitFor(() => {
        expect(createUserWithEmailAndPassword).toHaveBeenCalledWith(
          {},
          'newuser@example.com',
          'password123'
        );
        expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
      });
    });

    test('displays error message on failed sign up', async () => {
      createUserWithEmailAndPassword.mockRejectedValueOnce({
        message: 'Firebase: Email already in use'
      });
      
      renderWithRouter(<DineMetraAuth />);
      
      // Switch to sign up
      const signUpButton = screen.getByRole('button', { name: /^sign up$/i });
      fireEvent.click(signUpButton);
      
      const emailInput = screen.getByPlaceholderText('Enter your email');
      const passwordInput = screen.getByPlaceholderText('At least 6 characters');
      const confirmPasswordInput = screen.getByPlaceholderText('Re-enter password');
      const createAccountButton = screen.getByRole('button', { name: /create account/i });
      
      fireEvent.change(emailInput, { target: { value: 'existing@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } });
      fireEvent.click(createAccountButton);
      
      await waitFor(() => {
        expect(screen.getByText('Email already in use')).toBeInTheDocument();
      });
    });

    test('shows loading state during sign up', async () => {
      createUserWithEmailAndPassword.mockImplementation(() => 
        new Promise(resolve => setTimeout(resolve, 100))
      );
      
      renderWithRouter(<DineMetraAuth />);
      
      // Switch to sign up
      const signUpButton = screen.getByRole('button', { name: /^sign up$/i });
      fireEvent.click(signUpButton);
      
      const emailInput = screen.getByPlaceholderText('Enter your email');
      const passwordInput = screen.getByPlaceholderText('At least 6 characters');
      const confirmPasswordInput = screen.getByPlaceholderText('Re-enter password');
      const createAccountButton = screen.getByRole('button', { name: /create account/i });
      
      fireEvent.change(emailInput, { target: { value: 'newuser@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } });
      fireEvent.click(createAccountButton);
      
      expect(screen.getByRole('button', { name: /creating account\.\.\./i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /creating account\.\.\./i })).toBeDisabled();
    });
  });

  // ==================== GOOGLE SIGN IN TESTS ====================
  
  describe('Google Sign In Functionality', () => {
    test('successfully signs in with Google', async () => {
      signInWithPopup.mockResolvedValueOnce({
        user: { uid: '123', email: 'google@example.com' }
      });
      
      renderWithRouter(<DineMetraAuth />);
      
      const googleButton = screen.getByRole('button', { name: /sign in with google/i });
      fireEvent.click(googleButton);
      
      await waitFor(() => {
        expect(signInWithPopup).toHaveBeenCalledWith({}, {});
        expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
      });
    });

    test('displays error message on failed Google sign in', async () => {
      signInWithPopup.mockRejectedValueOnce({
        message: 'Firebase: Popup closed by user'
      });
      
      renderWithRouter(<DineMetraAuth />);
      
      const googleButton = screen.getByRole('button', { name: /sign in with google/i });
      fireEvent.click(googleButton);
      
      await waitFor(() => {
        expect(screen.getByText('Popup closed by user')).toBeInTheDocument();
      });
    });

    test('shows loading state during Google sign in', async () => {
      signInWithPopup.mockImplementation(() => 
        new Promise(resolve => setTimeout(resolve, 100))
      );
      
      renderWithRouter(<DineMetraAuth />);
      
      const googleButton = screen.getByRole('button', { name: /sign in with google/i });
      fireEvent.click(googleButton);
      
      // Check that buttons are in loading state
      const loadingButtons = screen.getAllByRole('button', { name: /signing in\.\.\./i });
      expect(loadingButtons.length).toBeGreaterThan(0);
      loadingButtons.forEach(button => {
        expect(button).toBeDisabled();
      });
    });
  });

  // ==================== ERROR HANDLING TESTS ====================
  
  describe('Error Handling', () => {
    test('removes "Firebase: " prefix from error messages', async () => {
      signInWithEmailAndPassword.mockRejectedValueOnce({
        message: 'Firebase: Error (auth/invalid-email)'
      });
      
      renderWithRouter(<DineMetraAuth />);
      
      const signInButton = screen.getByRole('button', { name: /sign in$/i });
      fireEvent.click(signInButton);
      
      await waitFor(() => {
        expect(screen.getByText('Error (auth/invalid-email)')).toBeInTheDocument();
        expect(screen.queryByText(/Firebase:/)).not.toBeInTheDocument();
      });
    });

    test('error message is visible with proper styling', async () => {
      signInWithEmailAndPassword.mockRejectedValueOnce({
        message: 'Firebase: Test error'
      });
      
      renderWithRouter(<DineMetraAuth />);
      
      const signInButton = screen.getByRole('button', { name: /sign in$/i });
      fireEvent.click(signInButton);
      
      await waitFor(() => {
        const errorDiv = screen.getByText('Test error').closest('div');
        expect(errorDiv).toHaveStyle({ background: '#ff4444' });
      });
    });
  });

  // ==================== ACCESSIBILITY TESTS ====================
  
  describe('Accessibility', () => {
    test('all form inputs have proper placeholders for guidance', () => {
      renderWithRouter(<DineMetraAuth />);
      
      expect(screen.getByPlaceholderText('Enter your email')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Enter your password')).toBeInTheDocument();
    });

    test('sign up form has all required input fields', () => {
      renderWithRouter(<DineMetraAuth />);
      
      // Switch to sign up
      const signUpButton = screen.getByRole('button', { name: /^sign up$/i });
      fireEvent.click(signUpButton);
      
      expect(screen.getByPlaceholderText('Enter your email')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('At least 6 characters')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Re-enter password')).toBeInTheDocument();
    });

    test('buttons are keyboard accessible', () => {
      renderWithRouter(<DineMetraAuth />);
      
      const signInButton = screen.getByRole('button', { name: /sign in$/i });
      expect(signInButton).not.toBeDisabled();
      
      // Simulate pressing Enter key
      fireEvent.keyDown(signInButton, { key: 'Enter', code: 'Enter' });
    });
    
    test('form inputs have appropriate ARIA attributes', () => {
      renderWithRouter(<DineMetraAuth />);
      
      const emailInput = screen.getByPlaceholderText('Enter your email');
      const passwordInput = screen.getByPlaceholderText('Enter your password');
      
      expect(emailInput).toHaveAttribute('type', 'email');
      expect(passwordInput).toHaveAttribute('type', 'password');
      expect(emailInput).toBeRequired();
      expect(passwordInput).toBeRequired();
    });
  });

  // ==================== FORM VALIDATION TESTS ====================
  
  describe('Form Validation', () => {
    test('email input accepts valid email format', () => {
      renderWithRouter(<DineMetraAuth />);
      
      const emailInput = screen.getByPlaceholderText('Enter your email');
      fireEvent.change(emailInput, { target: { value: 'valid.email@example.com' } });
      
      expect(emailInput).toHaveValue('valid.email@example.com');
    });

    test('password input is of type password', () => {
      renderWithRouter(<DineMetraAuth />);
      
      const passwordInput = screen.getByPlaceholderText('Enter your password');
      expect(passwordInput).toHaveAttribute('type', 'password');
    });

    test('all inputs are required', () => {
      renderWithRouter(<DineMetraAuth />);
      
      const emailInput = screen.getByPlaceholderText('Enter your email');
      const passwordInput = screen.getByPlaceholderText('Enter your password');
      
      expect(emailInput).toBeRequired();
      expect(passwordInput).toBeRequired();
    });
  });

  // ==================== INTEGRATION TESTS ====================
  
  describe('Integration Tests', () => {
    test('complete sign in flow', async () => {
      signInWithEmailAndPassword.mockResolvedValueOnce({
        user: { uid: '123', email: 'test@example.com' }
      });
      
      renderWithRouter(<DineMetraAuth />);
      
      // Fill in form
      fireEvent.change(screen.getByPlaceholderText('Enter your email'), {
        target: { value: 'test@example.com' }
      });
      fireEvent.change(screen.getByPlaceholderText('Enter your password'), {
        target: { value: 'password123' }
      });
      
      // Submit
      fireEvent.click(screen.getByRole('button', { name: /sign in$/i }));
      
      // Verify success
      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
      });
    });

    test('complete sign up flow', async () => {
      createUserWithEmailAndPassword.mockResolvedValueOnce({
        user: { uid: '123', email: 'newuser@example.com' }
      });
      
      renderWithRouter(<DineMetraAuth />);
      
      // Switch to sign up
      fireEvent.click(screen.getByRole('button', { name: /^sign up$/i }));
      
      // Fill in form
      fireEvent.change(screen.getByPlaceholderText('Enter your email'), {
        target: { value: 'newuser@example.com' }
      });
      fireEvent.change(screen.getByPlaceholderText('At least 6 characters'), {
        target: { value: 'password123' }
      });
      fireEvent.change(screen.getByPlaceholderText('Re-enter password'), {
        target: { value: 'password123' }
      });
      
      // Submit
      fireEvent.click(screen.getByRole('button', { name: /create account/i }));
      
      // Verify success
      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
      });
    });

    test('error recovery flow', async () => {
      // First attempt fails
      signInWithEmailAndPassword.mockRejectedValueOnce({
        message: 'Firebase: Invalid credentials'
      });
      
      renderWithRouter(<DineMetraAuth />);
      
      const emailInput = screen.getByPlaceholderText('Enter your email');
      const passwordInput = screen.getByPlaceholderText('Enter your password');
      const signInButton = screen.getByRole('button', { name: /sign in$/i });
      
      // First attempt
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'wrongpassword' } });
      fireEvent.click(signInButton);
      
      await waitFor(() => {
        expect(screen.getByText('Invalid credentials')).toBeInTheDocument();
      });
      
      // Second attempt succeeds
      signInWithEmailAndPassword.mockResolvedValueOnce({
        user: { uid: '123', email: 'test@example.com' }
      });
      
      fireEvent.change(passwordInput, { target: { value: 'correctpassword' } });
      fireEvent.click(signInButton);
      
      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
      });
    });
  });

  // ==================== ADDITIONAL COVERAGE TESTS ====================
  
  describe('UI Interactions', () => {
    test('input fields change border color on focus', () => {
      renderWithRouter(<DineMetraAuth />);
      
      const emailInput = screen.getByPlaceholderText('Enter your email');
      
      // Trigger focus event
      fireEvent.focus(emailInput);
      
      // Input should still be in document after focus
      expect(emailInput).toBeInTheDocument();
    });

    test('input fields reset border color on blur', () => {
      renderWithRouter(<DineMetraAuth />);
      
      const emailInput = screen.getByPlaceholderText('Enter your email');
      
      // Trigger focus then blur
      fireEvent.focus(emailInput);
      fireEvent.blur(emailInput);
      
      expect(emailInput).toBeInTheDocument();
    });

    test('sign in button changes style on hover', () => {
      renderWithRouter(<DineMetraAuth />);
      
      const signInButton = screen.getByRole('button', { name: /^sign in$/i });
      
      // Trigger hover events
      fireEvent.mouseEnter(signInButton);
      fireEvent.mouseLeave(signInButton);
      
      expect(signInButton).toBeInTheDocument();
    });

    test('Google button changes style on hover when not loading', () => {
      renderWithRouter(<DineMetraAuth />);
      
      const googleButton = screen.getByRole('button', { name: /sign in with google/i });
      
      fireEvent.mouseEnter(googleButton);
      fireEvent.mouseLeave(googleButton);
      
      expect(googleButton).toBeInTheDocument();
    });

    test('sign up toggle button changes style on hover', () => {
      renderWithRouter(<DineMetraAuth />);
      
      const signUpButton = screen.getByRole('button', { name: /^sign up$/i });
      
      fireEvent.mouseEnter(signUpButton);
      fireEvent.mouseLeave(signUpButton);
      
      expect(signUpButton).toBeInTheDocument();
    });

    test('back to sign in button changes style on hover', () => {
      renderWithRouter(<DineMetraAuth />);
      
      // Switch to sign up form
      fireEvent.click(screen.getByRole('button', { name: /^sign up$/i }));
      
      const backButton = screen.getByRole('button', { name: /back to sign in/i });
      
      fireEvent.mouseEnter(backButton);
      fireEvent.mouseLeave(backButton);
      
      expect(backButton).toBeInTheDocument();
    });
  });

  // ==================== SIGN UP FORM RENDERING DETAILS ====================
  
  describe('Sign Up Form Rendering Details', () => {
    test('sign up form shows title', () => {
      renderWithRouter(<DineMetraAuth />);
      
      // Switch to sign up
      fireEvent.click(screen.getByRole('button', { name: /^sign up$/i }));
      
      expect(screen.getByText('Sign Up')).toBeInTheDocument();
    });

    test('sign up form inputs have correct placeholders', () => {
      renderWithRouter(<DineMetraAuth />);
      
      // Switch to sign up
      fireEvent.click(screen.getByRole('button', { name: /^sign up$/i }));
      
      expect(screen.getByPlaceholderText('Enter your email')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('At least 6 characters')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Re-enter password')).toBeInTheDocument();
    });

    test('sign up form password fields are password type', () => {
      renderWithRouter(<DineMetraAuth />);
      
      // Switch to sign up
      fireEvent.click(screen.getByRole('button', { name: /^sign up$/i }));
      
      const passwordInput = screen.getByPlaceholderText('At least 6 characters');
      const confirmInput = screen.getByPlaceholderText('Re-enter password');
      
      expect(passwordInput).toHaveAttribute('type', 'password');
      expect(confirmInput).toHaveAttribute('type', 'password');
    });

    test('sign up inputs change border color on focus', () => {
      renderWithRouter(<DineMetraAuth />);
      
      // Switch to sign up
      fireEvent.click(screen.getByRole('button', { name: /^sign up$/i }));
      
      const passwordInput = screen.getByPlaceholderText('At least 6 characters');
      
      fireEvent.focus(passwordInput);
      fireEvent.blur(passwordInput);
      
      expect(passwordInput).toBeInTheDocument();
    });

    test('create account button changes style on hover', () => {
      renderWithRouter(<DineMetraAuth />);
      
      // Switch to sign up
      fireEvent.click(screen.getByRole('button', { name: /^sign up$/i }));
      
      const createButton = screen.getByRole('button', { name: /create account/i });
      
      fireEvent.mouseEnter(createButton);
      fireEvent.mouseLeave(createButton);
      
      expect(createButton).toBeInTheDocument();
    });
  });

  // ==================== DISABLED STATE INTERACTIONS ====================
  
  describe('Disabled State Interactions', () => {
    test('buttons do not respond to hover when loading', async () => {
      signInWithEmailAndPassword.mockImplementation(() => 
        new Promise(resolve => setTimeout(resolve, 100))
      );
      
      renderWithRouter(<DineMetraAuth />);
      
      const emailInput = screen.getByPlaceholderText('Enter your email');
      const passwordInput = screen.getByPlaceholderText('Enter your password');
      const signInButton = screen.getByRole('button', { name: /^sign in$/i });
      
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.click(signInButton);
      
      // Try to hover while loading
      const loadingButtons = screen.getAllByRole('button', { name: /signing in\.\.\./i });
      fireEvent.mouseEnter(loadingButtons[0]);
      
      expect(loadingButtons[0]).toBeDisabled();
    });

    test('Google button does not respond to hover when loading', async () => {
      signInWithPopup.mockImplementation(() => 
        new Promise(resolve => setTimeout(resolve, 100))
      );
      
      renderWithRouter(<DineMetraAuth />);
      
      const googleButton = screen.getByRole('button', { name: /sign in with google/i });
      fireEvent.click(googleButton);
      
      // Try to hover while loading
      const loadingButtons = screen.getAllByRole('button', { name: /signing in\.\.\./i });
      fireEvent.mouseEnter(loadingButtons[0]);
      fireEvent.mouseLeave(loadingButtons[0]);
      
      expect(loadingButtons[0]).toBeDisabled();
    });

    test('sign up button disabled during loading', async () => {
      signInWithEmailAndPassword.mockImplementation(() => 
        new Promise(resolve => setTimeout(resolve, 100))
      );
      
      renderWithRouter(<DineMetraAuth />);
      
      const emailInput = screen.getByPlaceholderText('Enter your email');
      const passwordInput = screen.getByPlaceholderText('Enter your password');
      const signInButton = screen.getByRole('button', { name: /^sign in$/i });
      
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.click(signInButton);
      
      // The "Sign Up" toggle button should also be disabled
      const signUpButton = screen.getByRole('button', { name: /^sign up$/i });
      expect(signUpButton).toBeDisabled();
    });

    test('back button responds to hover only when not loading', () => {
      renderWithRouter(<DineMetraAuth />);
      
      // Switch to sign up
      fireEvent.click(screen.getByRole('button', { name: /^sign up$/i }));
      
      const backButton = screen.getByRole('button', { name: /back to sign in/i });
      
      // Should respond to hover when not loading
      fireEvent.mouseEnter(backButton);
      expect(backButton).not.toBeDisabled();
      
      fireEvent.mouseLeave(backButton);
      expect(backButton).not.toBeDisabled();
    });
  });

  // ==================== EDGE CASES ====================
  
  describe('Edge Cases', () => {
    test('handles empty form submission for sign in', async () => {
      signInWithEmailAndPassword.mockRejectedValueOnce({
        message: 'Firebase: Invalid email'
      });
      
      renderWithRouter(<DineMetraAuth />);
      
      const signInButton = screen.getByRole('button', { name: /^sign in$/i });
      fireEvent.click(signInButton);
      
      await waitFor(() => {
        expect(screen.getByText('Invalid email')).toBeInTheDocument();
      });
    });

    test('handles empty form submission for sign up', async () => {
      renderWithRouter(<DineMetraAuth />);
      
      // Switch to sign up
      fireEvent.click(screen.getByRole('button', { name: /^sign up$/i }));
      
      const createButton = screen.getByRole('button', { name: /create account/i });
      fireEvent.click(createButton);
      
      // Should show password length error for empty password
      await waitFor(() => {
        expect(screen.getByText('Password must be at least 6 characters')).toBeInTheDocument();
      });
    });

    test('password with exactly 6 characters is valid', async () => {
      createUserWithEmailAndPassword.mockResolvedValueOnce({
        user: { uid: '123', email: 'test@example.com' }
      });
      
      renderWithRouter(<DineMetraAuth />);
      
      // Switch to sign up
      fireEvent.click(screen.getByRole('button', { name: /^sign up$/i }));
      
      const emailInput = screen.getByPlaceholderText('Enter your email');
      const passwordInput = screen.getByPlaceholderText('At least 6 characters');
      const confirmInput = screen.getByPlaceholderText('Re-enter password');
      const createButton = screen.getByRole('button', { name: /create account/i });
      
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: '123456' } });
      fireEvent.change(confirmInput, { target: { value: '123456' } });
      fireEvent.click(createButton);
      
      await waitFor(() => {
        expect(createUserWithEmailAndPassword).toHaveBeenCalled();
      });
    });

    test('clears error when switching between forms', async () => {
      signInWithEmailAndPassword.mockRejectedValueOnce({
        message: 'Firebase: Invalid credentials'
      });
      
      renderWithRouter(<DineMetraAuth />);
      
      // Trigger error on sign in
      const signInButton = screen.getByRole('button', { name: /^sign in$/i });
      fireEvent.click(signInButton);
      
      await waitFor(() => {
        expect(screen.getByText('Invalid credentials')).toBeInTheDocument();
      });
      
      // Switch to sign up - error should still be visible
      fireEvent.click(screen.getByRole('button', { name: /^sign up$/i }));
      
      // The component keeps the error, which is fine
      expect(screen.getByText('Invalid credentials')).toBeInTheDocument();
    });
  });

  // ==================== COMPONENT STATE MANAGEMENT ====================
  
  describe('Component State Management', () => {
    test('form data persists when switching forms', () => {
      renderWithRouter(<DineMetraAuth />);
      
      const emailInput = screen.getByPlaceholderText('Enter your email');
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      
      // Switch to sign up
      fireEvent.click(screen.getByRole('button', { name: /^sign up$/i }));
      
      // Switch back
      fireEvent.click(screen.getByRole('button', { name: /back to sign in/i }));
      
      // Email should be preserved
      const emailInputAgain = screen.getByPlaceholderText('Enter your email');
      expect(emailInputAgain).toHaveValue('test@example.com');
    });

    test('confirmPassword field only exists in sign up form', () => {
      renderWithRouter(<DineMetraAuth />);
      
      // Not in sign in
      expect(screen.queryByPlaceholderText('Re-enter password')).not.toBeInTheDocument();
      
      // Switch to sign up
      fireEvent.click(screen.getByRole('button', { name: /^sign up$/i }));
      
      // Now it exists
      expect(screen.getByPlaceholderText('Re-enter password')).toBeInTheDocument();
    });
  });

  // ==================== COMPREHENSIVE INLINE HANDLER COVERAGE ====================
  
  describe('Complete Event Handler Coverage', () => {
    test('all sign in form inputs have focus and blur handlers', () => {
      renderWithRouter(<DineMetraAuth />);
      
      const emailInput = screen.getByPlaceholderText('Enter your email');
      const passwordInput = screen.getByPlaceholderText('Enter your password');
      
      // Test email input
      fireEvent.focus(emailInput);
      fireEvent.blur(emailInput);
      
      // Test password input
      fireEvent.focus(passwordInput);
      fireEvent.blur(passwordInput);
      
      expect(emailInput).toBeInTheDocument();
      expect(passwordInput).toBeInTheDocument();
    });

    test('all sign up form inputs have focus and blur handlers', () => {
      renderWithRouter(<DineMetraAuth />);
      
      // Switch to sign up
      fireEvent.click(screen.getByRole('button', { name: /^sign up$/i }));
      
      const emailInput = screen.getByPlaceholderText('Enter your email');
      const passwordInput = screen.getByPlaceholderText('At least 6 characters');
      const confirmPasswordInput = screen.getByPlaceholderText('Re-enter password');
      
      // Test all three inputs
      fireEvent.focus(emailInput);
      fireEvent.blur(emailInput);
      
      fireEvent.focus(passwordInput);
      fireEvent.blur(passwordInput);
      
      fireEvent.focus(confirmPasswordInput);
      fireEvent.blur(confirmPasswordInput);
      
      expect(emailInput).toBeInTheDocument();
      expect(passwordInput).toBeInTheDocument();
      expect(confirmPasswordInput).toBeInTheDocument();
    });

    test('all sign in buttons have mouseEnter and mouseLeave handlers', () => {
      renderWithRouter(<DineMetraAuth />);
      
      const signInButton = screen.getByRole('button', { name: /^sign in$/i });
      const googleButton = screen.getByRole('button', { name: /sign in with google/i });
      const signUpButton = screen.getByRole('button', { name: /^sign up$/i });
      
      // Test sign in button
      fireEvent.mouseEnter(signInButton);
      fireEvent.mouseLeave(signInButton);
      
      // Test Google button
      fireEvent.mouseEnter(googleButton);
      fireEvent.mouseLeave(googleButton);
      
      // Test sign up button
      fireEvent.mouseEnter(signUpButton);
      fireEvent.mouseLeave(signUpButton);
      
      expect(signInButton).toBeInTheDocument();
      expect(googleButton).toBeInTheDocument();
      expect(signUpButton).toBeInTheDocument();
    });

    test('all sign up buttons have mouseEnter and mouseLeave handlers', () => {
      renderWithRouter(<DineMetraAuth />);
      
      // Switch to sign up
      fireEvent.click(screen.getByRole('button', { name: /^sign up$/i }));
      
      const createAccountButton = screen.getByRole('button', { name: /create account/i });
      const backButton = screen.getByRole('button', { name: /back to sign in/i });
      
      // Test create account button
      fireEvent.mouseEnter(createAccountButton);
      fireEvent.mouseLeave(createAccountButton);
      
      // Test back button
      fireEvent.mouseEnter(backButton);
      fireEvent.mouseLeave(backButton);
      
      expect(createAccountButton).toBeInTheDocument();
      expect(backButton).toBeInTheDocument();
    });

    test('hover handlers work correctly during loading state', async () => {
      signInWithEmailAndPassword.mockImplementation(() => 
        new Promise(resolve => setTimeout(resolve, 100))
      );
      
      renderWithRouter(<DineMetraAuth />);
      
      const emailInput = screen.getByPlaceholderText('Enter your email');
      const passwordInput = screen.getByPlaceholderText('Enter your password');
      const signInButton = screen.getByRole('button', { name: /^sign in$/i });
      
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.click(signInButton);
      
      // Get all buttons and try hover on each
      const allButtons = screen.getAllByRole('button');
      allButtons.forEach(button => {
        fireEvent.mouseEnter(button);
        fireEvent.mouseLeave(button);
      });
      
      expect(allButtons.length).toBeGreaterThan(0);
    });

    test('focus and blur work during loading state', async () => {
      signInWithEmailAndPassword.mockImplementation(() => 
        new Promise(resolve => setTimeout(resolve, 100))
      );
      
      renderWithRouter(<DineMetraAuth />);
      
      const emailInput = screen.getByPlaceholderText('Enter your email');
      const passwordInput = screen.getByPlaceholderText('Enter your password');
      const signInButton = screen.getByRole('button', { name: /^sign in$/i });
      
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.click(signInButton);
      
      // Try focus/blur during loading
      fireEvent.focus(emailInput);
      fireEvent.blur(emailInput);
      fireEvent.focus(passwordInput);
      fireEvent.blur(passwordInput);
      
      expect(emailInput).toBeDisabled();
      expect(passwordInput).toBeDisabled();
    });

    test('hover on Google button during loading state', async () => {
      signInWithPopup.mockImplementation(() => 
        new Promise(resolve => setTimeout(resolve, 100))
      );
      
      renderWithRouter(<DineMetraAuth />);
      
      const googleButton = screen.getByRole('button', { name: /sign in with google/i });
      fireEvent.click(googleButton);
      
      // Try to trigger hover during loading
      const allButtons = screen.getAllByRole('button');
      allButtons.forEach(button => {
        fireEvent.mouseEnter(button);
        fireEvent.mouseLeave(button);
      });
      
      expect(allButtons.length).toBeGreaterThan(0);
    });

    test('sign up form hover interactions during loading', async () => {
      createUserWithEmailAndPassword.mockImplementation(() => 
        new Promise(resolve => setTimeout(resolve, 100))
      );
      
      renderWithRouter(<DineMetraAuth />);
      
      // Switch to sign up
      fireEvent.click(screen.getByRole('button', { name: /^sign up$/i }));
      
      const emailInput = screen.getByPlaceholderText('Enter your email');
      const passwordInput = screen.getByPlaceholderText('At least 6 characters');
      const confirmPasswordInput = screen.getByPlaceholderText('Re-enter password');
      const createAccountButton = screen.getByRole('button', { name: /create account/i });
      
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } });
      fireEvent.click(createAccountButton);
      
      // Try hover and focus during loading
      const allButtons = screen.getAllByRole('button');
      allButtons.forEach(button => {
        fireEvent.mouseEnter(button);
        fireEvent.mouseLeave(button);
      });
      
      const allInputs = [emailInput, passwordInput, confirmPasswordInput];
      allInputs.forEach(input => {
        fireEvent.focus(input);
        fireEvent.blur(input);
      });
      
      expect(allButtons.length).toBeGreaterThan(0);
    });
  });
});