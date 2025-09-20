/**
 * API service for communicating with FastAPI backend
 * Handles all HTTP requests and authentication
 */

// API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * API service class to handle all backend communication
 */
class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  /**
   * Get authentication headers with JWT token
   * @returns {Object} Headers object with auth token if available
   */
  getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    return {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
    };
  }

  /**
   * Handle API response and errors
   * @param {Response} response - Fetch response object
   * @returns {Promise} Parsed JSON data or error
   */
  async handleResponse(response) {
    // Handle unauthorized - token expired
    if (response.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
      throw new Error('Session expired. Please login again.');
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    // Handle empty responses (204 No Content)
    if (response.status === 204) {
      return null;
    }

    return await response.json();
  }

  // ==================== AUTHENTICATION METHODS ====================

  /**
   * Register a new user
   * @param {Object} userData - User registration data
   * @returns {Promise} Registration response
   */
  async register(userData) {
    const response = await fetch(`${this.baseURL}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData),
    });
    return await this.handleResponse(response);
  }

  /**
   * Login user and get access token
   * @param {Object} loginData - Username and password
   * @returns {Promise} Login response with token
   */
  async login(loginData) {
    // FastAPI OAuth2PasswordRequestForm expects form data
    const formData = new FormData();
    formData.append('username', loginData.username);
    formData.append('password', loginData.password);

    const response = await fetch(`${this.baseURL}/api/auth/login`, {
      method: 'POST',
      body: formData,
    });
    return await this.handleResponse(response);
  }

  /**
   * Get current authenticated user information
   * @returns {Promise} User data
   */
  async getCurrentUser() {
    const response = await fetch(`${this.baseURL}/api/auth/me`, {
      headers: this.getAuthHeaders(),
    });
    return await this.handleResponse(response);
  }

  // ==================== SWEET MANAGEMENT METHODS ====================

  /**
   * Get all sweets from the inventory
   * @returns {Promise} Array of sweet objects
   */
  async getSweets() {
    const response = await fetch(`${this.baseURL}/api/sweets`, {
      headers: this.getAuthHeaders(),
    });
    return await this.handleResponse(response);
  }

  /**
   * Search sweets with filters
   * @param {Object} params - Search parameters (name, category, price range)
   * @returns {Promise} Array of filtered sweet objects
   */
  async searchSweets(params) {
    const queryString = new URLSearchParams();
    
    // Only add non-empty parameters to query string
    Object.keys(params).forEach(key => {
      if (params[key] !== undefined && params[key] !== null && params[key] !== '') {
        queryString.append(key, params[key]);
      }
    });

    const response = await fetch(`${this.baseURL}/api/sweets/search?${queryString}`, {
      headers: this.getAuthHeaders(),
    });
    return await this.handleResponse(response);
  }

  /**
   * Create a new sweet (Admin only)
   * @param {Object} sweetData - Sweet product data
   * @returns {Promise} Created sweet object
   */
  async createSweet(sweetData) {
    const response = await fetch(`${this.baseURL}/api/sweets`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(sweetData),
    });
    return await this.handleResponse(response);
  }

  /**
   * Update an existing sweet (Admin only)
   * @param {number} id - Sweet ID
   * @param {Object} sweetData - Updated sweet data
   * @returns {Promise} Updated sweet object
   */
  async updateSweet(id, sweetData) {
    const response = await fetch(`${this.baseURL}/api/sweets/${id}`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(sweetData),
    });
    return await this.handleResponse(response);
  }

  /**
   * Delete a sweet (Admin only)
   * @param {number} id - Sweet ID to delete
   * @returns {Promise} Delete confirmation
   */
  async deleteSweet(id) {
    const response = await fetch(`${this.baseURL}/api/sweets/${id}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders(),
    });
    return await this.handleResponse(response);
  }

  // ==================== INVENTORY OPERATIONS ====================

  /**
   * Purchase a sweet (reduce quantity)
   * @param {number} id - Sweet ID
   * @param {Object} purchaseData - Purchase details (quantity)
   * @returns {Promise} Purchase confirmation with total cost
   */
  async purchaseSweet(id, purchaseData) {
    const response = await fetch(`${this.baseURL}/api/sweets/${id}/purchase`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(purchaseData),
    });
    return await this.handleResponse(response);
  }

  /**
   * Restock a sweet (Admin only)
   * @param {number} id - Sweet ID
   * @param {Object} restockData - Restock details (quantity)
   * @returns {Promise} Restock confirmation
   */
  async restockSweet(id, restockData) {
    const response = await fetch(`${this.baseURL}/api/sweets/${id}/restock`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(restockData),
    });
    return await this.handleResponse(response);
  }

  // ==================== UTILITY METHODS ====================

  /**
   * Check if user is authenticated
   * @returns {boolean} True if access token exists
   */
  isAuthenticated() {
    return !!localStorage.getItem('access_token');
  }

  /**
   * Get stored user data from localStorage
   * @returns {Object|null} User object or null
   */
  getStoredUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }

  /**
   * Store authentication data in localStorage
   * @param {Object} tokens - Access token data
   * @param {Object} user - User data
   */
  storeAuthData(tokens, user) {
    localStorage.setItem('access_token', tokens.access_token);
    localStorage.setItem('user', JSON.stringify(user));
  }

  /**
   * Clear authentication data from localStorage
   */
  clearAuthData() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  }

  /**
   * Extract error message from error object
   * @param {Error} error - Error object
   * @returns {string} User-friendly error message
   */
  getErrorMessage(error) {
    if (error.message) {
      return error.message;
    }
    return 'An unexpected error occurred. Please try again.';
  }
}

// Create and export a single instance
const apiService = new ApiService();
export default apiService;