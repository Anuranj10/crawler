document.addEventListener('DOMContentLoaded', () => {
    // === Auth Management State ===
    let jwtToken = localStorage.getItem('jwt_token') || null;
    const authButtons = document.getElementById('authButtons');
    const userMenu = document.getElementById('userMenu');
    const userNameDisplay = document.getElementById('userNameDisplay');
    
    window.openModal = function(modalId) {
        document.getElementById(modalId).classList.remove('hide');
    }

    window.closeModal = function(modalId) {
        document.getElementById(modalId).classList.add('hide');
        document.getElementById(modalId.replace('Modal', 'Error')).classList.add('hide');
    }

    window.switchModal = function(fromId, toId) {
        closeModal(fromId);
        openModal(toId);
    }

    window.logout = function() {
        localStorage.removeItem('jwt_token');
        jwtToken = null;
        updateAuthUI();
        document.getElementById('profileForm').reset();
    }

    async function fetchUserProfile() {
        try {
            const response = await fetch('/api/user/me', {
                headers: { 'Authorization': `Bearer ${jwtToken}` }
            });
            if (response.ok) {
                const data = await response.json();
                userNameDisplay.textContent = `Hello, ${data.name.split(' ')[0]}`;
                document.getElementById('name').value = data.name || '';
                document.getElementById('email').value = data.email || '';
                if (data.education_level) document.getElementById('education_level').value = data.education_level;
                if (data.family_income) document.getElementById('family_income').value = data.family_income;
                if (data.category) document.getElementById('category').value = data.category;
                if (data.religion) document.getElementById('religion').value = data.religion;
                if (data.gender) {
                    const radio = document.querySelector(`input[name="gender"][value="${data.gender}"]`);
                    if (radio) radio.checked = true;
                }
            } else {
                logout();
            }
        } catch(err) {
            console.error(err);
        }
    }

    function updateAuthUI() {
        if (jwtToken) {
            authButtons.classList.add('hide');
            userMenu.classList.remove('hide');
            fetchUserProfile();
        } else {
            authButtons.classList.remove('hide');
            userMenu.classList.add('hide');
        }
    }

    updateAuthUI();

    // Login Form Handler
    document.getElementById('loginForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const fd = new FormData(e.target);
        const btn = e.target.querySelector('button');
        const spinner = document.getElementById('loginSpinner');
        const errorMsg = document.getElementById('loginError');
        
        btn.disabled = true;
        spinner.classList.remove('hide');
        errorMsg.classList.add('hide');

        try {
            const res = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(Object.fromEntries(fd))
            });
            const data = await res.json();
            if (res.ok) {
                jwtToken = data.access_token;
                localStorage.setItem('jwt_token', jwtToken);
                updateAuthUI();
                closeModal('loginModal');
                e.target.reset();
            } else {
                errorMsg.textContent = data.detail || "Login failed";
                errorMsg.classList.remove('hide');
            }
        } catch (err) {
            errorMsg.textContent = "Connection error";
            errorMsg.classList.remove('hide');
        } finally {
            btn.disabled = false;
            spinner.classList.add('hide');
        }
    });

    // Signup Form Handler
    document.getElementById('signupForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const fd = new FormData(e.target);
        const btn = e.target.querySelector('button');
        const spinner = document.getElementById('signupSpinner');
        const errorMsg = document.getElementById('signupError');
        
        // Confirm Password validation
        const pwd = document.getElementById('signupPassword').value;
        const confirmPwd = document.getElementById('signupConfirmPassword').value;
        if (pwd !== confirmPwd) {
            errorMsg.textContent = "Passwords do not match.";
            errorMsg.classList.remove('hide');
            return;
        }

        btn.disabled = true;
        spinner.classList.remove('hide');
        errorMsg.classList.add('hide');

        try {
            // Remove confirm_password from physical payload before sending to backend
            const payload = Object.fromEntries(fd);
            delete payload.confirm_password;
            
            const res = await fetch('/api/auth/signup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (res.ok) {
                closeModal('signupModal');
                openModal('loginModal'); // Prompt login
                e.target.reset();
            } else {
                errorMsg.textContent = data.detail || "Signup failed";
                errorMsg.classList.remove('hide');
            }
        } catch (err) {
            errorMsg.textContent = "Connection error";
            errorMsg.classList.remove('hide');
        } finally {
            btn.disabled = false;
            spinner.classList.add('hide');
        }
    });

    const form = document.getElementById('profileForm');
    const submitBtn = document.getElementById('submitBtn');
    const btnText = submitBtn.querySelector('.btn-text');
    const spinner = document.getElementById('loadingSpinner');
    const resultsSection = document.getElementById('resultsSection');
    const grid = document.getElementById('scholarshipsGrid');
    const matchCount = document.getElementById('matchCount');
    const docUpload = document.getElementById('document_upload');
    const uploadStatus = document.getElementById('uploadStatus');
    const statusText = uploadStatus.querySelector('.status-text');

    // Document Upload Handler (OCR Verification)
    docUpload.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        // UI Feedback
        uploadStatus.classList.remove('hide');
        uploadStatus.className = 'upload-status processing';
        statusText.textContent = "Analyzing document with AI...";

        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await fetch('/upload-document/', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.status === 'success') {
                uploadStatus.className = 'upload-status success';
                statusText.textContent = `Verified: ${data.document_type} (${data.confidence_score}% match)`;

                // Auto-fill fields if we detected them
                if (data.extracted_data.detected_income) {
                    document.getElementById('family_income').value = data.extracted_data.detected_income;
                }
                if (data.extracted_data.detected_category) {
                    document.getElementById('category').value = data.extracted_data.detected_category;
                }
            } else {
                uploadStatus.className = 'upload-status error';
                statusText.textContent = `Verification Failed: ${data.message}`;
            }
        } catch (error) {
            uploadStatus.className = 'upload-status error';
            statusText.textContent = "Connection error during verification.";
            console.error(error);
        }
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // 1. UI Loading State
        submitBtn.disabled = true;
        btnText.textContent = "Analyzing Profile...";
        spinner.classList.remove('hide');
        resultsSection.classList.add('hide');
        grid.innerHTML = "";

        // 2. Gather Data into JSON object exactly matching Pydantic UserProfile model
        const formData = new FormData(form);
        const userProfile = {
            name: formData.get('name'),
            email: formData.get('email'),
            education_level: formData.get('education_level'),
            family_income: parseFloat(formData.get('family_income')),
            category: formData.get('category'),
            religion: formData.get('religion'),
            gender: formData.get('gender')
        };

        try {
            // Optional: Save profile if logged in
            if (jwtToken) {
                fetch('/api/user/profile', {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${jwtToken}`
                    },
                    body: JSON.stringify(userProfile)
                }).catch(e => console.error("Could not save profile", e));
            }

            // 3. Make the API Call to our FastAPI backend
            const response = await fetch('/recommendations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(userProfile)
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.statusText}`);
            }

            const data = await response.json();

            // 4. Render Results
            renderMatches(data.matches);

        } catch (error) {
            console.error("Failed to fetch recommendations:", error);
            alert("Error connecting to the Recommendation Engine. Please try again.");
        } finally {
            // 5. Restore UI State
            submitBtn.disabled = false;
            btnText.textContent = "Find My Matches";
            spinner.classList.add('hide');
        }
    });

    function renderMatches(matches) {
        grid.innerHTML = '';

        if (!matches || matches.length === 0) {
            matchCount.textContent = "0 matches found";
            grid.innerHTML = `<p style="color: var(--text-dim); text-align: center; width: 100%;">No strong matches found for this specific profile. Try adjusting income thresholds or check back later!</p>`;
            resultsSection.classList.remove('hide');

            // Scroll to results cleanly
            resultsSection.scrollIntoView({ behavior: 'smooth' });
            return;
        }

        matchCount.textContent = `${matches.length} matches found`;

        matches.forEach(match => {
            const card = document.createElement('div');
            card.className = "scholarship-card";

            // Format score to a whole number visually and cap it 
            const displayScore = match.score > 100 ? "100" : Math.round(match.score);

            // Provide a fallback description if none exists
            const desc = match.description_snippet ?
                match.description_snippet.substring(0, 150) + "..." :
                "Click apply below to view full eligibility details and scholarship requirements.";

            // Safely parse application links array
            let applyUrl = match.url;
            try {
                const links = JSON.parse(match.application_links);
                if (links && links.length > 0) {
                    applyUrl = links[0]; // Take first direct apply link if available
                }
            } catch (e) { /* ignore JSON parse error */ }

            card.innerHTML = `
                <div class="card-header">
                    <span class="score-pip">${displayScore}% Match</span>
                </div>
                <h3>${match.title}</h3>
                <p>${desc}</p>
                <a href="${applyUrl}" target="_blank" class="apply-btn">View Details & Apply</a>
            `;

            grid.appendChild(card);
        });

        // Show the built grid with a smooth scroll
        resultsSection.classList.remove('hide');
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }
});
