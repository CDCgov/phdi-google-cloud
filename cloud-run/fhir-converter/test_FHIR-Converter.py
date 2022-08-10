from unittest import mock
import pytest
from main import convert_to_fhir


@mock.patch("main.vars")
@mock.patch("main.json.load")
@mock.patch("main.open")
@mock.patch("main.subprocess.run")
def test_convert_to_fhir(
    patched_subprocess_run, patched_open, patched_json_load, patched_vars
):

    # Prep dummy arguments values.
    template_directory_path = "my/path/to/Templates/subdirectory"
    root_template = "my-root-template"
    input_data_content = "my-message-content"
    input_data_file_path = "my/path/to/input/data/file"
    output_data_file_path = "my/path/to/output/data/file"
    converter_project_path = "my/path/to/converter/project"

    base_fhir_conversion_command = [
        "dotnet run ",
        f"--project {converter_project_path} ",
        "convert -- ",
        f"--TemplateDirectory {template_directory_path} ",
        f"--RootTemplate {root_template} ",
        f"--OutputDataFile {output_data_file_path} ",
    ]

    # Provide source data content directly with succesfull conversion.
    patched_subprocess_run.return_value = mock.Mock(returncode=0)
    convert_to_fhir(
        output_data_file_path,
        template_directory_path,
        converter_project_path,
        root_template,
        input_data_content=input_data_content,
    )
    fhir_conversion_command = (
        "".join(base_fhir_conversion_command)
        + f"--InputDataContent $'{input_data_content}'"
    )
    patched_subprocess_run.assert_called_with(
        fhir_conversion_command, shell=True, capture_output=True
    )
    patched_open.assert_called_with(output_data_file_path)

    # Provide file containing source data with unsuccesfull conversion.
    patched_subprocess_run.return_value = mock.Mock(returncode=1)
    convert_to_fhir(
        output_data_file_path,
        template_directory_path,
        converter_project_path,
        root_template,
        input_data_file_path=input_data_file_path,
    )
    fhir_conversion_command = (
        "".join(base_fhir_conversion_command)
        + f"--InputDataFile {input_data_file_path}"
    )
    patched_subprocess_run.assert_called_with(
        fhir_conversion_command, shell=True, capture_output=True
    )
    patched_vars.assert_called()

    # Ensure ValueError is reaised when neither input_data_content or
    # input_data_file_path are provided.
    with pytest.raises(ValueError):
        convert_to_fhir(
            output_data_file_path,
            template_directory_path,
            converter_project_path,
            root_template,
        )

    # Ensure ValueError is reaised when both input_data_content or input_data_file_path
    # are provided.
    with pytest.raises(ValueError):
        convert_to_fhir(
            output_data_file_path,
            template_directory_path,
            converter_project_path,
            root_template,
            input_data_content=input_data_content,
            input_data_file_path=input_data_file_path,
        )
