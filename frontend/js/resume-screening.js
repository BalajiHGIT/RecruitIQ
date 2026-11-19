
const API_BASE = "http://127.0.0.1:5000";

// Resume Upload and Screening
document.getElementById("resumeForm").addEventListener("submit", async function (event) {
    event.preventDefault();

    const candidateId = document.getElementById("candidateId").value;
    const jobId = document.getElementById("jobId").value;
    const resumeFile = document.getElementById("resumeFile").files[0];

    const message = document.getElementById("message");
    const result = document.getElementById("result");
    const uploadButton = document.getElementById("uploadButton");

    if (!resumeFile) {
        message.textContent = "Please select a resume.";
        return;
    }

    const allowedExtensions = [".pdf", ".docx"];
    const extension = resumeFile.name.substring(
        resumeFile.name.lastIndexOf(".")
    ).toLowerCase();

    if (!allowedExtensions.includes(extension)) {
        message.textContent = "Only PDF and DOCX files are allowed.";
        return;
    }

    if (resumeFile.size > 5 * 1024 * 1024) {
        message.textContent = "File size must be less than 5 MB.";
        return;
    }

    const formData = new FormData();
    formData.append("candidate_id", candidateId);
    formData.append("job_id", jobId);
    formData.append("resume", resumeFile);

    uploadButton.disabled = true;
    uploadButton.textContent = "Screening...";

    message.textContent = "Uploading and analyzing resume...";
    result.innerHTML = "";

    try {
        const response = await fetch(`${API_BASE}/api/resume-screening`, {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(data.message || "Resume screening failed.");
        }

        message.textContent = data.message;

        result.innerHTML = `
            <h3>Resume Screening Successful</h3>
            <h2>${Number(data.matching_score).toFixed(2)}%</h2>
            <p><strong>Screening ID:</strong> ${data.screening_id}</p>
            <p><strong>Candidate ID:</strong> ${candidateId}</p>
            <p><strong>Job ID:</strong> ${jobId}</p>
            <p><strong>Candidate Skills:</strong>
                ${data.candidate_skills.join(", ") || "None"}
            </p>
            <p><strong>Required Skills:</strong>
                ${data.required_skills.join(", ") || "None"}
            </p>
        `;

        await loadScreeningHistory();

    } catch (error) {
        message.textContent = error.message;
        result.textContent = "No screening result available.";
    } finally {
        uploadButton.disabled = false;
        uploadButton.textContent = "Upload & Screen Resume";
    }
});


// Load Screening History
async function loadScreeningHistory() {

    const history = document.getElementById("history");

    history.textContent = "Loading screening history...";

    try {
        const response = await fetch(`${API_BASE}/api/resume-screenings`);
        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(data.message || "Unable to load history.");
        }

        if (!data.screenings || data.screenings.length === 0) {
            history.textContent = "No screening records found.";
            return;
        }

        const table = document.createElement("table");

        table.innerHTML = `
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Candidate</th>
                    <th>Job</th>
                    <th>Resume</th>
                    <th>Match Score</th>
                    <th>Date</th>
                </tr>
            </thead>
            <tbody></tbody>
        `;

        const tbody = table.querySelector("tbody");

        data.screenings.forEach(item => {

            const row = document.createElement("tr");

            const values = [
                item.screening_id,
                item.full_name,
                item.job_title,
                item.resume_filename,
                `${Number(item.matching_score).toFixed(2)}%`,
                item.screening_date
            ];

            values.forEach(value => {
                const cell = document.createElement("td");
                cell.textContent = value ?? "";
                row.appendChild(cell);
            });

            tbody.appendChild(row);
        });

        history.replaceChildren(table);

    } catch (error) {
        history.textContent = error.message;
    }
}


// Refresh History Button
document.getElementById("refreshButton").addEventListener("click", loadScreeningHistory);


// Load history when page opens
document.addEventListener("DOMContentLoaded", loadScreeningHistory);
