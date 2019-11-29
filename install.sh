#!/usr/bin/env bash
# This is for installing source code only.

# Determine whether has Anaconda
CONDA=$(which conda)
# Determine which is the default package manager
APT=$(which apt)
PACMAN=$(which pacman)
DNF=$(which dnf)
YUM=$(which yum)
ZYPPER=$(which zypper)

# Title
echo ''
echo ''
echo '██╗  ██╗ █████╗ ██████╗ ██╗  ██╗███████╗███╗   ██╗'
echo '██║ ██╔╝██╔══██╗██╔══██╗██║ ██╔╝██╔════╝████╗  ██║'
echo '█████╔╝ ███████║██████╔╝█████╔╝ █████╗  ██╔██╗ ██║'
echo '██╔═██╗ ██╔══██║██╔══██╗██╔═██╗ ██╔══╝  ██║╚██╗██║'
echo '██║  ██╗██║  ██║██║  ██║██║  ██╗███████╗██║ ╚████║'
echo '╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝'
echo ''
echo 'github: https://github.com/ShawnHXH/Karken-KMB'
echo ''
echo ''

# Main:
while true; do
    echo 'Do you want dependencies to be installed in virtual environment(recommend)?'
    echo '- If you choose Yes, please ensure you have `conda` (Anaconda).'
    echo '- If you choose No, then will jump to next step.'
    echo 'Please input [Y/n]: '
    read ans

    if [[ ${#ans} -eq 0 || $ans = "Y" || $ans = "y" ]]; then
        # install in virtual environment by conda
        while True; do
            if [[ ${#CONDA} -gt 0 ]]; then
                echo 'A new env named `karken-kmb` will be created, continue? [Y/n]'
                read ans
                if [[ $ans = "Y" || $ans = "y" ]]; then
                    # requirements will be installed also
                    sudo conda create -n karken-kmb python=3.6 lxml=4.3.2 pyyaml=5.1.2 PyQt
                elif [[ $ans = "N" || $ans = "n" ]]; then
                    echo 'You still can create your own env, following:'
                    echo ''
                    echo '      `conda create -n <YOUR_ENV_NAME> python=3.6(RECOMMEND)`'
                    echo '      `conda activate <YOUR_NEW_NAME>`'
                    echo '      `pip install -r requirements.txt`'
                    echo '      `conda deactivate`'
                    echo ''
                    echo 'Having fun with Karken: KMB.'
                    exit 1
                fi
            else
                echo 'Please install Anaconda then retry.'
                exit 1
            fi
            echo 'Note: The latest version of PyQt that `conda` installed may NOT be 5.13.0.'
            echo 'If this version of PyQt works not very well, following:'
            echo ''
            echo '      `conda activate karken-kmb`'
            echo '      `conda remove PyQt`'
            echo '         `pip install PyQt5==5.13.0`'
            echo '         or'
            echo '         `pip install -r requirements.txt`'
            echo '      `conda deactivate`'
            echo ''
            echo 'then retry.'
            echo 'Having fun with Karken: KMB.'

            [[ ${#ans} -eq 0 || $ans = "Y" || $ans = "y" || $ans = "N" || $ans = "n" ]] && break;
        done

    elif [[ $ans = "N" || $ans = "n" ]]; then
        # install in local or global environment.
        # install python3 and pip3 if not exist
        echo 'Python3 will be installed if not exist.'
        if [[ ${#APT} -gt 0 ]]; then
            sudo apt-get install python3
            sudo apt-get install python3-pip
        elif [[ ${#PACMAN} -gt 0 ]]; then
            sudo pacman -S python3
            sudo pacman -S python3-pip
        elif [[ ${#DNF} -gt 0 ]]; then
            sudo dnf install python3
            sudo dnf install python3-pip
        elif [[ ${#YUM} -gt 0 ]]; then
            sudo yum install python3
            sudo yum install python3-pip
        elif [[ ${#ZYPPER} -gt 0 ]]; then
            sudo zypper install python3
            sudo zypper install python3-pip
        else
            echo "Unknown package manager. Download one of the following:"
            echo "  apt, pacman, dnf, yum or zypper"
            echo ""
            exit 1
        fi

        # install the all the necessary packages and requirements.
        echo ''
        while true; do
            echo 'Do you want dependencies to be installed globally (or locally) [Y/n]?'
            read ans
            if [[ ${#ans} -eq 0 || $ans = "Y" || $ans = "y" ]]; then
                sudo pip3 install --upgrade setuptools
                sudo pip3 install -r requirements.txt
            elif [[ $ans = "N" || $ans = "n" ]]; then
                sudo pip3 install --user --upgrade setuptools
                sudo pip3 install --user -r requirements.txt
            fi

            [[ ${#ans} -eq 0 || $ans = "Y" || $ans = "y" || $ans = "N" || $ans = "n" ]] && break;
        done
    fi

    [[ ${#ans} -eq 0 || $ans = "Y" || $ans = "y" || $ans = "N" || $ans = "n" ]] && break;
done
