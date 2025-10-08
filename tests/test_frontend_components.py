import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import axios from 'axios';
import App from '../src/App';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('ASK_GILLU Frontend Tests', () => {
  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();
  });

  test('renders ASK_GILLU title', () => {
    render(<App />);
    const titleElement = screen.getByText(/ASK_GILLU/i);
    expect(titleElement).toBeInTheDocument();
  });

  test('renders SRMU description', () => {
    render(<App />);
    const descriptionElement = screen.getByText(/Your SRMU AI Assistant/i);
    expect(descriptionElement).toBeInTheDocument();
  });

  test('renders question input field', () => {
    render(<App />);
    const inputElement = screen.getByPlaceholderText(/Enter your question about SRMU/i);
    expect(inputElement).toBeInTheDocument();
  });

  test('renders web search toggle', () => {
    render(<App />);
    const toggleElement = screen.getByText(/Include Web Search/i);
    expect(toggleElement).toBeInTheDocument();
  });

  test('web search toggle works correctly', () => {
    render(<App />);
    const toggleCheckbox = screen.getByRole('checkbox');
    
    // Initially unchecked
    expect(toggleCheckbox).not.toBeChecked();
    
    // Click to check
    fireEvent.click(toggleCheckbox);
    expect(toggleCheckbox).toBeChecked();
    
    // Click to uncheck
    fireEvent.click(toggleCheckbox);
    expect(toggleCheckbox).not.toBeChecked();
  });

  test('displays different messages based on web search toggle', () => {
    render(<App />);
    const toggleCheckbox = screen.getByRole('checkbox');
    
    // Initially should show document-only message
    expect(screen.getByText(/Searching only SRMU documents/i)).toBeInTheDocument();
    
    // Toggle web search on
    fireEvent.click(toggleCheckbox);
    expect(screen.getByText(/Searching both SRMU documents and the internet/i)).toBeInTheDocument();
  });

  test('submit button is disabled when question is empty', () => {
    render(<App />);
    const submitButton = screen.getByRole('button', { name: /Ask/i });
    
    expect(submitButton).toBeDisabled();
  });

  test('submit button is enabled when question is entered', () => {
    render(<App />);
    const inputElement = screen.getByPlaceholderText(/Enter your question about SRMU/i);
    const submitButton = screen.getByRole('button', { name: /Ask/i });
    
    // Type a question
    fireEvent.change(inputElement, { target: { value: 'What is SRMU?' } });
    
    // Mock successful status response
    mockedAxios.get.mockResolvedValueOnce({
      data: { status: 'ready', message: 'Ready' }
    });
    
    expect(submitButton).not.toBeDisabled();
  });

  test('form submission sends correct data', async () => {
    render(<App />);
    const inputElement = screen.getByPlaceholderText(/Enter your question about SRMU/i);
    const submitButton = screen.getByRole('button', { name: /Ask/i });
    const toggleCheckbox = screen.getByRole('checkbox');
    
    // Mock successful responses
    mockedAxios.get.mockResolvedValueOnce({
      data: { status: 'ready', message: 'Ready' }
    });
    
    mockedAxios.post.mockResolvedValueOnce({
      data: { answer: 'Test answer' }
    });
    
    // Enter question and enable web search
    fireEvent.change(inputElement, { target: { value: 'What is SRMU?' } });
    fireEvent.click(toggleCheckbox);
    
    // Submit form
    fireEvent.click(submitButton);
    
    // Wait for the API call
    await waitFor(() => {
      expect(mockedAxios.post).toHaveBeenCalledWith(
        'http://localhost:8000/ask',
        expect.any(FormData),
        expect.objectContaining({
          headers: { 'Content-Type': 'multipart/form-data' },
          timeout: 30000
        })
      );
    });
  });

  test('displays loading state during API call', async () => {
    render(<App />);
    const inputElement = screen.getByPlaceholderText(/Enter your question about SRMU/i);
    const submitButton = screen.getByRole('button', { name: /Ask/i });
    
    // Mock API responses
    mockedAxios.get.mockResolvedValueOnce({
      data: { status: 'ready', message: 'Ready' }
    });
    
    // Mock a delayed response
    mockedAxios.post.mockImplementationOnce(
      () => new Promise(resolve => setTimeout(() => resolve({ data: { answer: 'Test answer' } }), 1000))
    );
    
    // Enter question and submit
    fireEvent.change(inputElement, { target: { value: 'What is SRMU?' } });
    fireEvent.click(submitButton);
    
    // Should show loading state
    await waitFor(() => {
      expect(screen.getByText(/Thinking.../i)).toBeInTheDocument();
    });
  });

  test('displays answer after successful API call', async () => {
    render(<App />);
    const inputElement = screen.getByPlaceholderText(/Enter your question about SRMU/i);
    const submitButton = screen.getByRole('button', { name: /Ask/i });
    
    // Mock successful responses
    mockedAxios.get.mockResolvedValueOnce({
      data: { status: 'ready', message: 'Ready' }
    });
    
    mockedAxios.post.mockResolvedValueOnce({
      data: { answer: 'SRMU is a great university!' }
    });
    
    // Enter question and submit
    fireEvent.change(inputElement, { target: { value: 'What is SRMU?' } });
    fireEvent.click(submitButton);
    
    // Wait for answer to appear
    await waitFor(() => {
      expect(screen.getByText(/SRMU is a great university!/i)).toBeInTheDocument();
    });
  });

  test('displays error message on API failure', async () => {
    render(<App />);
    const inputElement = screen.getByPlaceholderText(/Enter your question about SRMU/i);
    const submitButton = screen.getByRole('button', { name: /Ask/i });
    
    // Mock status success but API failure
    mockedAxios.get.mockResolvedValueOnce({
      data: { status: 'ready', message: 'Ready' }
    });
    
    mockedAxios.post.mockRejectedValueOnce(new Error('Network error'));
    
    // Enter question and submit
    fireEvent.change(inputElement, { target: { value: 'What is SRMU?' } });
    fireEvent.click(submitButton);
    
    // Wait for error message
    await waitFor(() => {
      expect(screen.getByText(/An error occurred while getting the answer/i)).toBeInTheDocument();
    });
  });

  test('prompt customization works', () => {
    render(<App />);
    
    // Find and click the settings button to expand prompt section
    const settingsButton = screen.getByText(/Customize AI Response Style/i);
    fireEvent.click(settingsButton);
    
    // Check if prompt template dropdown is visible
    const templateSelect = screen.getByDisplayValue(/Default/i);
    expect(templateSelect).toBeInTheDocument();
    
    // Change template
    fireEvent.change(templateSelect, { target: { value: 'Casual' } });
    
    // Check if it changed
    expect(templateSelect).toHaveValue('Casual');
  });

  test('status indicator shows correct states', () => {
    render(<App />);
    
    // Mock different status responses
    mockedAxios.get.mockResolvedValueOnce({
      data: { status: 'ready', message: 'System ready' }
    });
    
    // Should show ready status
    waitFor(() => {
      expect(screen.getByText(/System ready/i)).toBeInTheDocument();
    });
  });
});

// Integration Tests
describe('ASK_GILLU Integration Tests', () => {
  test('end-to-end user workflow', async () => {
    render(<App />);
    
    // Mock all API calls
    mockedAxios.get.mockResolvedValueOnce({
      data: { status: 'ready', message: 'Ready' }
    });
    
    mockedAxios.post.mockResolvedValueOnce({
      data: { answer: '## SRMU Information\n\nSRMU is a prestigious university.' }
    });
    
    // 1. User sees the interface
    expect(screen.getByText(/ASK_GILLU/i)).toBeInTheDocument();
    
    // 2. User enables web search
    const toggleCheckbox = screen.getByRole('checkbox');
    fireEvent.click(toggleCheckbox);
    
    // 3. User types a question
    const inputElement = screen.getByPlaceholderText(/Enter your question about SRMU/i);
    fireEvent.change(inputElement, { target: { value: 'What is SRMU?' } });
    
    // 4. User submits the question
    const submitButton = screen.getByRole('button', { name: /Ask/i });
    fireEvent.click(submitButton);
    
    // 5. User sees the answer
    await waitFor(() => {
      expect(screen.getByText(/SRMU is a prestigious university/i)).toBeInTheDocument();
    });
  });
});
