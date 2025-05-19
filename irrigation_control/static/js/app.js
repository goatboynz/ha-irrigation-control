// API Client functions
const API = {
    async request(endpoint, options = {}) {
        try {
            const response = await fetch(endpoint, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'API request failed');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            showAlert(error.message, 'danger');
            throw error;
        }
    },

    // Solenoid endpoints
    async getSwitches() {
        return this.request('/api/ha-switches');
    },

    async getSolenoids() {
        return this.request('/api/solenoids');
    },

    async createSolenoid(data) {
        return this.request('/api/solenoids', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    async deleteSolenoid(id) {
        return this.request(`/api/solenoids/${id}`, {
            method: 'DELETE'
        });
    },

    async controlSolenoid(id, action) {
        return this.request(`/api/solenoids/${id}/control?action=${action}`, {
            method: 'POST'
        });
    },

    // Group endpoints
    async getGroups() {
        return this.request('/api/groups');
    },

    async createGroup(data) {
        return this.request('/api/groups', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    async updateGroup(id, data) {
        return this.request(`/api/groups/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    async deleteGroup(id) {
        return this.request(`/api/groups/${id}`, {
            method: 'DELETE'
        });
    },

    // Schedule endpoints
    async getSchedules() {
        return this.request('/api/schedules');
    },

    async createSchedule(data) {
        return this.request('/api/schedules', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    async updateSchedule(id, data) {
        return this.request(`/api/schedules/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    async deleteSchedule(id) {
        return this.request(`/api/schedules/${id}`, {
            method: 'DELETE'
        });
    },

    async runSchedule(id) {
        return this.request(`/api/schedules/${id}/run`, {
            method: 'POST'
        });
    }
};

// UI Helper functions
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;

    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);

    setTimeout(() => alertDiv.remove(), 5000);
}

function formatTime(timeString) {
    return new Date(`1970-01-01T${timeString}`).toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit'
    });
}

function createTimeSlotRow() {
    return `
        <div class="time-slot-row">
            <input type="time" name="start_time" required>
            <input type="number" name="duration_minutes" min="1" max="360" required>
            <div class="days-of-week">
                <label><input type="checkbox" value="MON"> Mon</label>
                <label><input type="checkbox" value="TUE"> Tue</label>
                <label><input type="checkbox" value="WED"> Wed</label>
                <label><input type="checkbox" value="THU"> Thu</label>
                <label><input type="checkbox" value="FRI"> Fri</label>
                <label><input type="checkbox" value="SAT"> Sat</label>
                <label><input type="checkbox" value="SUN"> Sun</label>
            </div>
            <button type="button" class="btn btn-danger remove-slot">Remove</button>
        </div>
    `;
}

// Event Handlers
document.addEventListener('DOMContentLoaded', () => {
    // Common event handlers
    document.addEventListener('click', async (e) => {
        // Handle solenoid control buttons
        if (e.target.matches('.control-solenoid')) {
            const id = e.target.dataset.id;
            const action = e.target.dataset.action;
            try {
                await API.controlSolenoid(id, action);
                showAlert(`Solenoid ${action === 'turn_on' ? 'started' : 'stopped'} successfully`, 'success');
            } catch (error) {
                // Error already handled by API.request
            }
        }

        // Handle schedule run buttons
        if (e.target.matches('.run-schedule')) {
            const id = e.target.dataset.id;
            try {
                await API.runSchedule(id);
                showAlert('Schedule started successfully', 'success');
            } catch (error) {
                // Error already handled by API.request
            }
        }

        // Handle delete buttons
        if (e.target.matches('.delete-item')) {
            if (!confirm('Are you sure you want to delete this item?')) {
                return;
            }

            const type = e.target.dataset.type;
            const id = e.target.dataset.id;
            try {
                switch (type) {
                    case 'solenoid':
                        await API.deleteSolenoid(id);
                        break;
                    case 'group':
                        await API.deleteGroup(id);
                        break;
                    case 'schedule':
                        await API.deleteSchedule(id);
                        break;
                }
                e.target.closest('.card').remove();
                showAlert('Item deleted successfully', 'success');
            } catch (error) {
                // Error already handled by API.request
            }
        }
    });

    // Initialize time slot handlers if on schedule form
    const addSlotButton = document.querySelector('.add-time-slot');
    if (addSlotButton) {
        addSlotButton.addEventListener('click', () => {
            const slotsContainer = document.querySelector('.time-slots');
            slotsContainer.insertAdjacentHTML('beforeend', createTimeSlotRow());
        });

        // Handle remove slot button clicks
        document.addEventListener('click', (e) => {
            if (e.target.matches('.remove-slot')) {
                e.target.closest('.time-slot-row').remove();
            }
        });
    }
});

// Form helper functions
function getFormData(form) {
    const formData = new FormData(form);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        if (key.includes('[]')) {
            key = key.replace('[]', '');
            if (!data[key]) {
                data[key] = [];
            }
            data[key].push(value);
        } else {
            data[key] = value;
        }
    }
    
    return data;
}

function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;

    requiredFields.forEach(field => {
        if (!field.value) {
            isValid = false;
            field.classList.add('error');
        } else {
            field.classList.remove('error');
        }
    });

    return isValid;
}
