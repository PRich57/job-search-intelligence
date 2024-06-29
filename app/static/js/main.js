// Main JavaScript file for Job Listings Viewer

document.addEventListener("DOMContentLoaded", function() {
    let table;
    let selectedTitles = [];

    // Initialize DataTable
    function initializeDataTable() {
        table = $("#jobTable").DataTable({
            ajax: {
                url: "/api/jobs",
                dataSrc: "data",
                data: function(d) {
                    d.titles = selectedTitles;
                },
                error: function(xhr, error, thrown) {
                    console.error("Error:", error);
                    console.error("Response:", xhr.responseText);
                    $("#error-message").text("An error occurred while loading the data. Please try refreshing the page.");
                }
            },
            columns: [
                { data: "job_title" },
                { data: "company_name" },
                { data: "job_location" },
                { data: "salary_range" },
                { data: "source" }
            ],
            pageLength: 25,
            order: [[0, "asc"]],
            dom: "lBfrtip",
            buttons: ["copy", "csv", "excel", "pdf", "print"]
        });
    }

    // Load job titles and populate filter
    function loadJobTitles() {
        fetch("/api/job_titles")
            .then(response => response.json())
            .then(data => {
                const filterContainer = document.getElementById("titleFilter");
                data.titles.forEach(title => {
                    const checkbox = document.createElement("input");
                    checkbox.type = "checkbox";
                    checkbox.id = `title-${title}`;
                    checkbox.value = title;
                    checkbox.addEventListener("change", handleTitleFilterChange);

                    const label = document.createElement("label");
                    label.htmlFor = `title-${title}`;
                    label.textContent = title;

                    filterContainer.appendChild(checkbox);
                    filterContainer.appendChild(label);
                    filterContainer.appendChild(document.createElement("br"));
                });
            });
    }

    // Handle title filter changes
    function handleTitleFilterChange(event) {
        const title = event.target.value;
        if (event.target.checked) {
            selectedTitles.push(title);
        } else {
            const index = selectedTitles.indexOf(title);
            if (index > -1) {
                selectedTitles.splice(index, 1);
            }
        }
        table.ajax.reload();
    }

    // Initialize modal functionality
    function initializeModal() {
        const modal = document.getElementById("jobModal");
        const closeBtn = document.getElementsByClassName("close")[0];

        $("#jobTable tbody").on("click", "tr", function() {
            const data = table.row(this).data();
            $("#modalJobTitle").text(data.job_title);
            $("#modalCompany").text(data.company_name);
            $("#modalLocation").text(data.job_location);
            $("#modalSource").text(data.source);
            $("#modalSalary").text(data.salary_range);
            $("#modalApplyLink").attr("href", data.application_url);
            $("#modalDescription").text(data.job_description);
            modal.style.display = "block";
        });

        closeBtn.onclick = function() {
            modal.style.display = "none";
        };

        window.onclick = function(event) {
            if (event.target == modal) {
                modal.style.display = "none";
            }
        };
    }

    // Initialize the application
    function initialize() {
        initializeDataTable();
        loadJobTitles();
        initializeModal();
    }

    initialize();
});