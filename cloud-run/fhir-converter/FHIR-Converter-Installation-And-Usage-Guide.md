# Microsoft FHIR Converter CLI Installation Guide
This document provides a guide for installing the [Microsoft FHIR Converter](https://github.com/microsoft/FHIR-Converter) as a Command Line Interface (CLI) tool on MacOS and Linux (*.nix) systems and a brief introduction to using the converter.

## Install the .NET Framework
We will use .NET to build the FHIR Converter from source code. Follow the steps to below to install .NET. If .NET is already installed skip to [Download and Build the FHIR Converter](#download-and-build-the-fhir-converter). To check if .NET is installed trying running `dotnet`, if documentation about using .NET is displayed then it is installed. A response indicating that the command was not found suggests that .NET is not installed.  

### Download the .NET Install Script
Run `wget https://dotnet.microsoft.com/download/dotnet/scripts/v1/dotnet-install.sh` to download the .NET installation script from Microsoft.

### Install .NET
From the directory containing the `dotnet-install.sh` file, downloaded in the previous step, run `sh ./dotnet-install.sh` to execute the script and install .NET.

### Add .NET to the PATH Environment Variable
Finally, add .NET to you PATH variable by running `export PATH="$PATH:$HOME/.dotnet"`.

### Confirm That .NET has Been Installed.
Restart your shell with `exec $SHELL` and then run `dotnet`. If you get a response that looks like what is shown below, .NET was installed successfully.

>Usage: dotnet [options]
>Usage: dotnet [path-to-application]
>
>Options:  
>  -h|--help         Display help.  
>  --info            Display .NET Core information.  
>  --list-sdks       Display the installed SDKs.  
>  --list-runtimes   Display the installed runtimes.  
>
>path-to-application:  
>  The path to an application .dll file to execute.  

## Download and Build the FHIR Converter

### Get Microsoft FHIR Converter
Clone the Microsfot FHIR Converter source code from GitHub with a command like this one that downloads the 5.0.4 release (most recent at the time of writing). 
`git clone https://github.com/microsoft/FHIR-Converter.git --branch v5.0.4 --single-branch`

### Build the FHIR Converter Tool
Navigate to `.../FHIR-Converter/src/Microsoft.Health.Fhir.Liquid.Converter.Tool` and run `dotnet build` to build the FHIR Converter. 

## Using the FHIR Converter

Two examples have been provided below of using the FHIR Converter via the `dotnet run` function. Please note that `--` is used to deliminate between arguments that should be passed to `dotnet` as opposed arguments that `dotnet` should be pass to the application, in this case the FHIR Converter, that it is  being used to run. Additionaly, the `-p` option is only required when not calling `dotnet run` from the `FHIR-Converter/src/Health.Fhir.Liquid.Converter.Tool/` directory. For additional information on `dotnet run` please refer to [this documentation from Microsoft](https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-run).

### Message in File to FHIR
The following command can be used to convert a message from a file to FHIR.
`dotnet run convert -p path-to-Microsoft.Health.Fhir.Liquid.Converter.Tool/ -- -d path-to-template subdirectory-for-message-type -r root-template -n path-to-file-to-be-converted -f path-to-output`

### Covert Message Content Directory to FHIR
The following command can be used to convert the contents of a message provided directly as a string to FHIR.
`dotnet run convert -p path-to-Microsoft.Health.Fhir.Liquid.Converter.Tool/ -- -d path-to-template subdirectory-for-message-type -r root-template -c message-content -f path-to-output`