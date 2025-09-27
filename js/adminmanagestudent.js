document.addEventListener("DOMContentLoaded", function () {
    // Get CSRF token
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content || '';
    
    // Helper function to preserve data types
    function parseValue(value, originalType) {
        if (value === '') return null;
        
        // Try to infer the type
        if (!isNaN(value) && value.trim() !== '') {
            if (value.includes('.')) return parseFloat(value);
            return parseInt(value);
        }
        
        // Handle boolean values
        if (value.toLowerCase() === 'true') return true;
        if (value.toLowerCase() === 'false') return false;
        
        // Handle date format
        if (/^\d{4}-\d{2}-\d{2}/.test(value)) {
            const date = new Date(value);
            if (!isNaN(date.getTime())) return value; // Keep as string for ISO dates
        }
        
        return value;
    }
    
    // Handle photo upload button clicks
    document.querySelectorAll(".upload-photo-btn").forEach(button => {
        button.addEventListener("click", function() {
            const fileInput = this.closest('.photo-cell').querySelector('.photo-upload');
            fileInput.click();
        });
    });
    
    // Handle file selection
    document.querySelectorAll(".photo-upload").forEach(input => {
        input.addEventListener("change", function() {
            if (this.files && this.files[0]) {
                const cell = this.closest('.photo-cell');
                const img = cell.querySelector('.student-photo') || document.createElement('img');
                
                if (!cell.querySelector('.student-photo')) {
                    cell.querySelector('.no-photo')?.remove();
                    img.classList.add('student-photo');
                    img.width = 50;
                    img.height = 50;
                    img.alt = "Student Photo";
                    cell.insertBefore(img, cell.firstChild);
                }
                
                const reader = new FileReader();
                reader.onload = function(e) {
                    img.src = e.target.result;
                    img.setAttribute('data-base64', e.target.result);
                    
                    // Mark the row as having a changed photo
                    const row = cell.closest('tr');
                    row.setAttribute('data-photo-changed', 'true');
                };
                reader.readAsDataURL(this.files[0]);
            }
        });
    });
    
    // Save button handler
    document.querySelectorAll(".save-btn").forEach(button => {
        button.addEventListener("click", function () {
            let row = this.closest("tr");
            let id = row.getAttribute("data-id");
            let cells = row.querySelectorAll("td[data-column]");
            let updatedData = {};
            
            cells.forEach(cell => {
                let key = cell.getAttribute('data-column');
                
                if (key === 'photo') {
                    // Only include photo data if it was changed
                    if (row.getAttribute('data-photo-changed') === 'true') {
                        const img = cell.querySelector('.student-photo');
                        const photoData = img?.getAttribute('data-base64');
                        if (photoData) {
                            updatedData[key] = photoData;
                        }
                    }
                } else if (cell.getAttribute('contenteditable') === 'true') {
                    updatedData[key] = parseValue(cell.innerText.trim());
                }
            });

            // Show processing indicator
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            this.disabled = true;

            fetch("/update-student/" + id, {
                method: "POST",
                headers: { 
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },
                body: JSON.stringify(updatedData)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Show success message
                this.innerHTML = '<i class="fas fa-check"></i>';
                // Reset the photo changed flag
                row.removeAttribute('data-photo-changed');
                setTimeout(() => {
                    this.innerHTML = 'Save';
                    this.disabled = false;
                }, 1500);
            })
            .catch(error => {
                console.error("Error:", error);
                this.innerHTML = '<i class="fas fa-times"></i>';
                setTimeout(() => {
                    this.innerHTML = 'Save';
                    this.disabled = false;
                }, 1500);
                alert("Error saving changes: " + error.message);
            });
        });
    });

    // Delete button handler
    document.querySelectorAll(".delete-btn").forEach(button => {
        button.addEventListener("click", function () {
            if (!confirm("Are you sure you want to delete this student?")) {
                return;
            }
            
            let row = this.closest("tr");
            let id = row.getAttribute("data-id");
            
            // Show processing indicator
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            this.disabled = true;

            fetch("/delete-student/" + id, { 
                method: "DELETE",
                headers: {
                    "X-CSRFToken": csrfToken
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                row.remove();
                updateStudentCount();
            })
            .catch(error => {
                console.error("Error:", error);
                this.innerHTML = 'Delete';
                this.disabled = false;
                alert("Error deleting student: " + error.message);
            });
        });
    });

    // PDF Download Handler
    document.getElementById('downloadPdfButton').addEventListener('click', function() {
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF('landscape');
        
        // Get table data and PDF logo
        const table = document.getElementById('studentTable');
        const logoElement = document.querySelector('.pdf-logo');
        const rows = table.querySelectorAll('tbody tr');
        
        // Prepare data for PDF
        const tableData = [];
        const headers = Array.from(table.querySelectorAll('thead th'))
            .slice(0, -1) // Exclude the last 'Actions' column
            .filter(th => th.textContent.trim() !== 'Photo' && th.textContent.trim() !== 'photo') // Exclude Photo column
            .map(th => th.textContent.trim());

        rows.forEach((row) => {
            const rowData = [];
            const cells = row.querySelectorAll('td[data-column]');
            
            cells.forEach(cell => {
                // Skip the last column (Actions), Photo column, and ensure we're not including photo
                if (cell.getAttribute('data-column') !== null && 
                    cell.getAttribute('data-column') !== 'actions' &&
                    cell.getAttribute('data-column') !== 'photo' &&
                    cell.getAttribute('data-column') !== 'Photo') {
                    
                    rowData.push(cell.textContent.trim());
                }
            });
            
            tableData.push(rowData);
        });
        
        // Wait for logo to load (if available)
        const logoPromise = new Promise((resolve) => {
            if (logoElement && logoElement.src) {
                const logo = new Image();
                logo.onload = () => resolve(logo);
                logo.onerror = () => resolve(null);
                logo.src = logoElement.src;
            } else {
                resolve(null);
            }
        });

        logoPromise.then((logo) => {
            // Add logo if available
            if (logo) {
                const pageWidth = doc.internal.pageSize.getWidth();
                const pageHeight = doc.internal.pageSize.getHeight();
                
                const maxLogoWidth = pageWidth * 0.8;
                const logoAspectRatio = logo.width / logo.height;
                const logoWidth = Math.min(logo.width, maxLogoWidth);
                const logoHeight = logoWidth / logoAspectRatio;
                
                const logoX = (pageWidth - logoWidth) / 2 + 50;
                const logoY = 20;
                
                doc.addImage(logo, 'JPEG', logoX, logoY, logoWidth, logoHeight);
                
                // Add separator line
                const lineY = logoY + logoHeight + 10;
                doc.setLineWidth(0.5);
                doc.line(20, lineY, pageWidth - 20, lineY);
                
                
                // Add page title
                doc.setFontSize(16);
                doc.setTextColor(50, 50, 50);
                doc.text('Student Details Report', pageWidth / 2, lineY + 25, { align: 'center' });
                const titleWidth = doc.getTextWidth('Student Details Report');
                const titleX = (pageWidth - titleWidth) / 2;
                const titleY = lineY + 26;
                
                doc.setLineWidth(0.5);
                doc.line(titleX, titleY, titleX + titleWidth, titleY);
            }
            
            // Generate table
            doc.autoTable({
                head: [headers],
                body: tableData,
                startY: logo ? 100 : 30,
                styles: {
                    fontSize: 9,
                    cellPadding: 2,
                    overflow: 'linebreak'
                },
                columnStyles: {
                    0: { cellWidth: 'auto' }
                }
            });
            
            // Save the PDF
            doc.save('student_details.pdf');
        });
    });

    // -------------------- SEARCH AND FILTER FUNCTIONALITY --------------------
    
    // Get DOM elements
    const searchInput = document.getElementById('searchInput');
    const searchButton = document.getElementById('searchButton');
    const busFilter = document.getElementById('busFilter');
    const semesterFilter = document.getElementById('semesterFilter');
    const resetFiltersButton = document.getElementById('resetFilters');
    const studentTable = document.getElementById('studentTable');
    const noResultsMessage = document.getElementById('noResults');
    
    // NEW: Get delete all buttons
    const deleteAllButton = document.getElementById('deleteAllButton');
    const deleteFilteredButton = document.getElementById('deleteFilteredButton');
    
    // Initialize filter values
    let availableBuses = new Set();
    let availableSemesters = new Set();
    
    // Populate the filter dropdowns from the table data
    function populateFilterOptions() {
        // Clear existing options (keeping the first "All" option)
        while (busFilter.options.length > 1) {
            busFilter.remove(1);
        }
        while (semesterFilter.options.length > 1) {
            semesterFilter.remove(1);
        }
        
        // Reset sets
        availableBuses.clear();
        availableSemesters.clear();
        
        // Get all rows except the header
        const rows = Array.from(studentTable.querySelectorAll('tbody tr'));
        
        // Extract unique values for bus_no and semester
        rows.forEach(row => {
            const busNoCell = row.querySelector('td[data-column="bus_no"]');
            const semesterCell = row.querySelector('td[data-column="semester"]');
            
            if (busNoCell) {
                const busNo = busNoCell.textContent.trim();
                if (busNo) availableBuses.add(busNo);
            }
            
            if (semesterCell) {
                const semester = semesterCell.textContent.trim();
                if (semester) availableSemesters.add(semester);
            }
        });
        
        // Sort the sets
        const sortedBuses = Array.from(availableBuses).sort();
        const sortedSemesters = Array.from(availableSemesters).sort((a, b) => {
            // Try to convert to numbers for proper sorting
            const numA = parseInt(a);
            const numB = parseInt(b);
            if (!isNaN(numA) && !isNaN(numB)) {
                return numA - numB;
            }
            return a.localeCompare(b);
        });
        
        // Add options to the dropdowns
        sortedBuses.forEach(bus => {
            const option = document.createElement('option');
            option.value = bus;
            option.textContent = bus;
            busFilter.appendChild(option);
        });
        
        sortedSemesters.forEach(semester => {
            const option = document.createElement('option');
            option.value = semester;
            option.textContent = semester;
            semesterFilter.appendChild(option);
        });
    }

    // Function to update student count
    function updateStudentCount() {
        const studentTable = document.getElementById('studentTable');
        const studentCountDisplay = document.getElementById('studentCountDisplay');
        
        // Count total rows in the table body after filtering
        const totalStudents = Array.from(studentTable.querySelectorAll('tbody tr'))
            .filter(row => row.style.display !== 'none').length;
        
        // Update the display with filtered student count
        studentCountDisplay.textContent = `Total Students: ${totalStudents}`;
    }
    
    // Filter and search function
    function filterAndSearchTable() {
        const searchTerm = searchInput.value.toLowerCase().trim();
        const busValue = busFilter.value;
        const semesterValue = semesterFilter.value;
        
        // Get all rows except the header
        const rows = Array.from(studentTable.querySelectorAll('tbody tr'));
        let visibleCount = 0;
        
        rows.forEach(row => {
            // Check filter conditions
            let matchesBusFilter = true;
            let matchesSemesterFilter = true;
            
            // Check bus filter
            if (busValue) {
                const busCell = row.querySelector('td[data-column="bus_no"]');
                if (busCell && busCell.textContent.trim() !== busValue) {
                    matchesBusFilter = false;
                }
            }
            
            // Check semester filter
            if (semesterValue) {
                const semesterCell = row.querySelector('td[data-column="semester"]');
                if (semesterCell && semesterCell.textContent.trim() !== semesterValue) {
                    matchesSemesterFilter = false;
                }
            }
            
            // Check search term (if provided)
            let matchesSearch = searchTerm === '';
            
            if (!matchesSearch) {
                // Check all cells in the row for the search term
                const cells = Array.from(row.querySelectorAll('td[data-column]'));
                
                matchesSearch = cells.some(cell => {
                    // Skip cells with images
                    if (cell.classList.contains('photo-cell')) return false;
                    
                    const cellText = cell.textContent.toLowerCase();
                    return cellText.includes(searchTerm);
                });
            }
            
            // Show or hide row based on all conditions
            const shouldShow = matchesBusFilter && matchesSemesterFilter && matchesSearch;
            row.style.display = shouldShow ? '' : 'none';
            
            if (shouldShow) visibleCount++;
        });
        
        // Show/hide no results message
        noResultsMessage.style.display = visibleCount === 0 ? 'block' : 'none';

        updateStudentCount();
        
        // Update the delete filtered button state
        updateDeleteFilteredButtonState(visibleCount);
    }
    
    // Update delete filtered button state based on visible records
    function updateDeleteFilteredButtonState(visibleCount) {
        if (deleteFilteredButton) {
            deleteFilteredButton.disabled = visibleCount === 0;
        }
    }
    
    // Event listeners for filters
    busFilter.addEventListener('change', filterAndSearchTable);
    semesterFilter.addEventListener('change', filterAndSearchTable);
    
    // Event listeners for search
    searchInput.addEventListener('keyup', function(e) {
        if (e.key === 'Enter') {
            filterAndSearchTable();
        }
    });
    
    searchButton.addEventListener('click', filterAndSearchTable);
    
    // Reset filters
    resetFiltersButton.addEventListener('click', function() {
        searchInput.value = '';
        busFilter.value = '';
        semesterFilter.value = '';
        
        // Reset the table
        filterAndSearchTable();
    });
    
    // Delete All Students Handler
    if (deleteAllButton) {
        deleteAllButton.addEventListener('click', function() {
            const totalStudents = studentTable.querySelectorAll('tbody tr').length;
            
            if (totalStudents === 0) {
                alert("No students to delete.");
                return;
            }
            
            if (!confirm(`Are you sure you want to delete ALL ${totalStudents} student records? This action cannot be undone.`)) {
                return;
            }
            
            // Show processing indicator
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Deleting...';
            this.disabled = true;
            
            fetch("/delete-all-students", {
                method: "DELETE",
                headers: {
                    "X-CSRFToken": csrfToken
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Clear the table body
                const tbody = studentTable.querySelector('tbody');
                tbody.innerHTML = '';

                updateStudentCount();
                
                // Show success message
                alert(`Successfully deleted ${data.deletedCount} student records.`);
                
                // Reset button
                this.innerHTML = 'Delete All Students';
                this.disabled = false;
                
                // Show no results message
                noResultsMessage.style.display = 'block';
                
                // Update filter options
                populateFilterOptions();
            })
            .catch(error => {
                console.error("Error:", error);
                this.innerHTML = 'Delete All Students';
                this.disabled = false;
                alert("Error deleting students: " + error.message);
            });
        });
    }
    
    // Delete Filtered Students Handler
    if (deleteFilteredButton) {
        deleteFilteredButton.addEventListener('click', function() {
            const searchTerm = searchInput.value.toLowerCase().trim();
            const busValue = busFilter.value;
            const semesterValue = semesterFilter.value;
            
            // Count visible (filtered) students
            const visibleStudents = Array.from(studentTable.querySelectorAll('tbody tr'))
                .filter(row => row.style.display !== 'none');
            
            if (visibleStudents.length === 0) {
                alert("No visible students to delete.");
                return;
            }
            
            let confirmMessage = `Are you sure you want to delete ${visibleStudents.length} filtered student records?`;
            
            // Add filter details to confirmation message
            if (semesterValue) {
                confirmMessage += `\n- Semester: ${semesterValue}`;
            }
            if (busValue) {
                confirmMessage += `\n- Bus No: ${busValue}`;
            }
            if (searchTerm) {
                confirmMessage += `\n- Search: "${searchTerm}"`;
            }
            
            confirmMessage += "\n\nThis action cannot be undone.";
            
            if (!confirm(confirmMessage)) {
                return;
            }
            
            // Collect IDs of visible students
            const studentIds = visibleStudents.map(row => row.getAttribute('data-id'));
            
            // Show processing indicator
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Deleting...';
            this.disabled = true;
            
            // Prepare filter criteria for the server
            const filterCriteria = {
                studentIds: studentIds,
                filters: {
                    semester: semesterValue || null,
                    busNo: busValue || null,
                    searchTerm: searchTerm || null
                }
            };
            
            fetch("/delete-filtered-students", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },
                body: JSON.stringify(filterCriteria)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Remove deleted rows from the table
                visibleStudents.forEach(row => row.remove());

                updateStudentCount();
                
                // Show success message
                alert(`Successfully deleted ${data.deletedCount} student records.`);
                
                // Reset button
                this.innerHTML = 'Delete Filtered Students';
                this.disabled = false;
                
                // Update visible count
                const remainingVisible = studentTable.querySelectorAll('tbody tr[style=""]').length;
                if (remainingVisible === 0) {
                    noResultsMessage.style.display = 'block';
                }
                
                // Update filter options
                populateFilterOptions();
                filterAndSearchTable();
            })
            .catch(error => {
                console.error("Error:", error);
                this.innerHTML = 'Delete Filtered Students';
                this.disabled = false;
                alert("Error deleting students: " + error.message);
            });
        });
    }

    updateStudentCount();
    
    // Initialize the page
    populateFilterOptions();
    
    // Initial update of delete filtered button state
    const initialVisibleCount = Array.from(studentTable.querySelectorAll('tbody tr'))
        .filter(row => row.style.display !== 'none').length;
    updateDeleteFilteredButtonState(initialVisibleCount);

    
});