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

    // Load job titles and populate dropdown
    function loadJobTitles() {
        fetch("/api/job_titles")
            .then(response => response.json())
            .then(data => {
                const selectElement = document.getElementById("titleFilter");
                if (selectElement) {
                    data.titles.forEach(title => {
                        const option = document.createElement("option");
                        option.value = title;
                        option.textContent = title;
                        selectElement.appendChild(option);
                    });
                    
                    // Initialize Select2
                    $(selectElement).select2({
                        placeholder: "Select job titles",
                        allowClear: true
                    });

                    // Add event listener for changes
                    $(selectElement).on('change', handleTitleFilterChange);
                } else {
                    console.error("Title filter select element not found");
                }
            })
            .catch(error => {
                console.error("Error loading job titles:", error);
            });
    }

    // Handle title filter changes
    function handleTitleFilterChange(e) {
        selectedTitles = $(e.target).val() || [];
        if (table) {
            table.ajax.reload();
        }
    }

    // Initialize modal functionality
    function initializeModal() {
        const modal = document.getElementById("jobModal");
        const closeBtn = document.getElementsByClassName("close")[0];

        if (modal && closeBtn) {
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
        } else {
            console.error("Modal or close button not found");
        }
    }

    function setupFetchButton() {
        const fetchButton = document.getElementById("fetchButton")
        if (fetchButton) {
            fetchButton.addEventListener("click", function() {
                console.log("Fetching all jobs...")
                fetch("/api/fetch_all_jobs")
                    .then(response => response.json())
                    .then(data => {
                        console.log("Adzuna response:", data.adzuna);
                        console.log("USA Jobs response:", data.usa_jobs);
                        console.log("Total jobs fetched:", data.job_count);
                    })
                    .catch(error => {
                        console.error("Error fetching jobs:", error);
                    });
            });
        } else {
            console.error("Fetch button not found");
        }
    }

    // Initialize the application
    function initialize() {
        initializeDataTable();
        loadJobTitles();
        initializeModal();
        setupFetchButton();
    }

    initialize();
});