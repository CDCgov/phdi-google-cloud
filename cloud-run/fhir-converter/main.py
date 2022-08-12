from pathlib import Path
import subprocess
import json

from fastapi import FastAPI
from pydantic import BaseModel

api = FastAPI()


class FhirConverterInput(BaseModel):
    """
    Input parameters for the FHIR Converter.
    """

    input_data: str
    input_type: str
    root_template: str


@api.get("/")
async def root():
    return {"status": "OK"}


@api.post("/convert-to-fhir")
async def convert(input: FhirConverterInput):
    return convert_to_fhir(**dict(input))


def convert_to_fhir(
    input_data: str,
    input_type: str,
    root_template: str,
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

    :param input_data: The message to be converted as a string.
    :param input_type: The type of message to be converted. Valid values are "hl7v2" and "c-cda".
    :param root_template: Name of the liquid template within to be used for conversion.
        Options are listed in the FHIR-Converter README.md.
    """

    # Setup path variables
    converter_project_path = "/build/FHIR-Converter/src/Microsoft.Health.Fhir.Liquid.Converter.Tool"
    if input_type == "hl7v2":
        template_directory_path = "/build/FHIR-Converter/data/Templates/Hl7v2"
    elif input_type == "c-cda":
        template_directory_path = "/build/FHIR-Converter/data/Templates/Ccda"
    else:
        raise ValueError(
            f"Invalid input_type {input_type}. Valid values are 'hl7v2' and 'c-cda'."
        )
    output_data_file_path = "/tmp/output.json"

    # Write input data to file
    input_data_file_path = Path(f"/tmp/{input_type}-input.txt")
    input_data_file_path.write_text(input_data)

    # Formulate command for the FHIR Converter.
    fhir_conversion_command = [
        "dotnet run ",
        f"--project {converter_project_path} ",
        "convert -- ",
        f"--TemplateDirectory {template_directory_path} ",
        f"--RootTemplate {root_template} ",
        f"--InputDataFile {str(input_data_file_path)} "
        f"--OutputDataFile {str(output_data_file_path)} ",
    ]

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
