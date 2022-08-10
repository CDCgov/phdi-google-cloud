from pathlib import Path
from typing import Union, Optional
import subprocess
import json


def convert_to_fhir(
    output_data_file_path: Union[str, Path],
    template_directory_path: Union[str, Path],
    converter_project_path: Union[str, Path],
    root_template: str,
    input_data_content: Optional[str] = None,
    input_data_file_path: Optional[Union[str, Path]] = None,
) -> dict:
    """
    Call the Microsoft FHIR Converter CLI tool to convert an Hl7v2, or C-CDA message
    to FHIR R4. The message to be converted can be provided either as a string via the
    input_data_content argument, or by specifying a path to a file containing the
    message with input_data_file_path. One, but not both of these parameters is
    required. When conversion is successfull a dictionary containing the resulting FHIR
    bundle is returned. When conversion fails a dictionary containing the response from
    the FHIR Converter is returned. In order to successfully call this function,
    the conversion tool must be installed. For information on how to do this please
    refer to FHIR-Converter-Installation-And-Usage-Guide. The source code for the
    converter can be found at https://github.com/microsoft/FHIR-Converter.

    :param output_file_path: The complete path for the output file containing the FHIR
        bundle produced by the conversion.
    :param template_directory_path: Path to the Templates/ subdirectory within the FHIR
        Converter for data type to be converted (Ccda/, Hl7v2/, Json/, or Stu3ToR4/).
    :param converter_project_path: Path to the
        Microsoft.Health.Fhir.Liquid.Converter.Tool/ directory within the FHIR
        converter.
    :param root_template: Name of the liquid template within the template_direcotry_path
        to be used for conversion, excluding the '.liquid' extension. Options are listed
        in the FHIR-Converter README.md.
    :param input_data_content: The message to be converted as a string.
    :param input_data_file_path: The complete path to a file containing a single message
        to convert to FHIR.
    """

    # Ensure either input_data_content or input_data_file_path has been provided.
    if input_data_content is None and input_data_file_path is None:
        raise ValueError(
            "A value for input_data_content or input_data_file_path must be provided."
        )
    if input_data_content is not None and input_data_file_path is not None:
        raise ValueError(
            "Both input_data_content or input_data_file_path cannot be specified. "
        )

    # Ensure all paths are pathlib objects not strings.
    for path in [
        input_data_file_path,
        output_data_file_path,
        template_directory_path,
        converter_project_path,
    ]:
        if type(path) == str:
            path = Path(path)

    # Forumlate command for the FHIR Converter.
    fhir_conversion_command = [
        "dotnet run ",
        f"--project {str(converter_project_path)} ",
        "convert -- ",
        f"--TemplateDirectory {str(template_directory_path)} ",
        f"--RootTemplate {root_template} ",
        f"--OutputDataFile {str(output_data_file_path)} ",
    ]

    if input_data_content is not None:
        fhir_conversion_command.append(f"--InputDataContent $'{input_data_content}'")
    else:
        fhir_conversion_command.append(f"--InputDataFile {str(input_data_file_path)}")

    fhir_conversion_command = "".join(fhir_conversion_command)

    # Call the FHIR Converter.
    converter_response = subprocess.run(
        fhir_conversion_command, shell=True, capture_output=True
    )

    # Process the response from FHIR Converter.
    if converter_response.returncode == 0:
        result = json.load(open(output_data_file_path))
    else:
        result = vars(converter_response)

    return result
