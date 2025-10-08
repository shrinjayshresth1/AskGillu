import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import axios from 'axios';
import App from '../src/App';

// Mock axios
jest.mock('axios');
const mockedAxios = axios;

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
});
