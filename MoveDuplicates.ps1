# Define paths
$duplicateBasePath = "C:\Users\Admin\Downloads"
$keepFolder = "$duplicateBasePath\Duplicate\To_Review_Keep"
$deleteFolder = "$duplicateBasePath\Duplicate\To_Review_Delete"

# Duplicate file groups data (file paths)
$duplicateGroups = @(
    @("C:\Users\Admin\Downloads\Corporate_Emergency_Response_Plan_Almansour_Engineering.docx", "C:\Users\Admin\Downloads\Documents\Corporate_Emergency_Response_Plan_Almansour_Engineering.docx", "C:\Users\Admin\Downloads\Documents\Corporate_Emergency_Response_Plan_Almansour_Engineering_1.docx", "C:\Users\Admin\Downloads\Documents\Corporate_Emergency_Response_Plan_Almansour_Engineering_1_1.docx"),
    @("C:\Users\Admin\Downloads\INCIDENT REPORT- BUILDING E- JACKHAMMER- TAIWO JELILI.pdf", "C:\Users\Admin\Downloads\Documents\INCIDENT REPORT- BUILDING E- JACKHAMMER- TAIWO JELILI.pdf", "C:\Users\Admin\Downloads\Documents\INCIDENT REPORT- BUILDING E- JACKHAMMER- TAIWO JELILI_1.pdf", "C:\Users\Admin\Downloads\Documents\INCIDENT REPORT- BUILDING E- JACKHAMMER- TAIWO JELILI_1_1.pdf"),
    @("C:\Users\Admin\Downloads\langflow_safety_assistant_fixed_final(1).json", "C:\Users\Admin\Downloads\langflow_safety_assistant_fixed_final.json"),
    @("C:\Users\Admin\Downloads\NE1-00-HS-SEC-PLN-OOO(G)-00006-09.docx", "C:\Users\Admin\Downloads\Documents\NE1-00-HS-SEC-PLN-OOO(G)-00006-09.docx", 
"C:\Users\Admin\Downloads\Documents\NE1-00-HS-SEC-PLN-OOO(G)-00006-09_1.docx", "C:\Users\Admin\Downloads\Documents\NE1-00-HS-SEC-PLN-OOO(G)-00006-09_1_1.docx"),
    @("C:\Users\Admin\Downloads\Payloader_31_Day_PreWork_Checklist.pdf", "C:\Users\Admin\Downloads\Documents\Payloader_31_Day_PreWork_Checklist.pdf", 
"C:\Users\Admin\Downloads\Documents\Payloader_31_Day_PreWork_Checklist_1.pdf", "C:\Users\Admin\Downloads\Documents\Payloader_31_Day_PreWork_Checklist_1_1.pdf")
    # Add other duplicate groups here similarly if needed
)

foreach ($group in $duplicateGroups) {
    # Move the first file to To_Review_Keep
    $fileToKeep = $group[0]
    if (Test-Path $fileToKeep) {
        Move-Item -Path $fileToKeep -Destination $keepFolder -Force        
    }
    # Move the rest of the files to To_Review_Delete
    $filesToDelete = $group[1..($group.Count - 1)]
    foreach ($file in $filesToDelete) {
        if (Test-Path $file) {
            Move-Item -Path $file -Destination $deleteFolder -Force        
        }
    }
}

Write-Host "Files moved successfully. Please review the 'To_Review_Keep' and 'To_Review_Delete' folders."