/**
 * API Client - Handles all frontend API communication
 * Provides centralized, reusable methods for backend requests
 */

class APIClient {
    constructor(baseURL = '') {
        this.baseURL = baseURL || window.location.origin;
        this.defaultHeaders = {
            'Content-Type': 'application/json',
        };
    }

    /**
     * Make an API request
     * @param {string} endpoint - API endpoint
     * @param {Object} options - Request options
     * @returns {Promise<Object>} Response data
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                ...this.defaultHeaders,
                ...options.headers,
            },
            ...options,
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new APIError(
                    data.message || 'API request failed',
                    response.status,
                    data
                );
            }

            return data;
        } catch (error) {
            if (error instanceof APIError) {
                throw error;
            }
            throw new APIError('Network error', 0, error);
        }
    }

    /**
     * GET request
     * @param {string} endpoint - API endpoint
     * @returns {Promise<Object>}
     */
    async get(endpoint) {
        return this.request(endpoint, {
            method: 'GET',
        });
    }

    /**
     * POST request
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Request body
     * @returns {Promise<Object>}
     */
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    /**
     * PUT request
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Request body
     * @returns {Promise<Object>}
     */
    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    /**
     * DELETE request
     * @param {string} endpoint - API endpoint
     * @returns {Promise<Object>}
     */
    async delete(endpoint) {
        return this.request(endpoint, {
            method: 'DELETE',
        });
    }
}

/**
 * Custom API Error class
 */
class APIError extends Error {
    constructor(message, status, data) {
        super(message);
        this.name = 'APIError';
        this.status = status;
        this.data = data;
    }
}

/**
 * Badminton API Client - Specific methods for badminton endpoints
 */
class BadmintonAPIClient extends APIClient {
    /**
     * Save a match result
     * @param {Array<string>} winners - Winner names
     * @param {Array<string>} losers - Loser names
     * @param {string} type - 'singles' or 'doubles'
     * @returns {Promise<Object>}
     */
    async saveMatch(winners, losers, type) {
        return this.post('/api/save-match', {
            winners,
            losers,
            type,
        });
    }

    /**
     * Get updated rankings
     * @returns {Promise<Object>}
     */
    async getRankings() {
        return this.get('/update-rankings');
    }

    /**
     * Get updated likes
     * @returns {Promise<Object>}
     */
    async getLikes() {
        return this.get('/update-likes');
    }

    /**
     * Get updated comments
     * @returns {Promise<Object>}
     */
    async getComments() {
        return this.get('/update-comments');
    }

    /**
     * Add a like
     * @returns {Promise<Object>}
     */
    async addLike() {
        return this.post('/like', {});
    }

    /**
     * Add a comment/wish
     * @param {string} author - Author name
     * @param {string} text - Comment text
     * @returns {Promise<Object>}
     */
    async addComment(author, text) {
        const formData = new FormData();
        formData.append('author', author);
        formData.append('comment_text', text);

        return this.request('/comment', {
            method: 'POST',
            body: formData,
            headers: {}, // Remove Content-Type to let browser set it
        });
    }
}

// Create global API client instance
window.api = new BadmintonAPIClient();
