# utils/dependency_checker.py
import importlib
import subprocess
import sys
import platform

class DependencyChecker:
    """
    Utility class to check and install required dependencies for the clinic management system
    """
    
    @staticmethod
    def check_dependencies():
        """
        Check if all required dependencies are installed
        Returns a tuple: (all_installed, missing_packages)
        """
        required_packages = {
            "PySide6": "6.0.0",  # Minimum version
            "docx": "0.2.4",  # For report generation
            "argon2-cffi": "21.0.0",  # For password hashing
            # Add any other dependencies your application requires
        }
        
        missing_packages = []
        
        for package, min_version in required_packages.items():
            try:
                # Try to import the package
                module = importlib.import_module(package)
                
                # Some packages have different __version__ attribute names
                version = None
                for attr in ["__version__", "VERSION", "version"]:
                    if hasattr(module, attr):
                        version = getattr(module, attr)
                        break
                
                # Check if we need to do a more specific import for the version
                if version is None and package == "docx":
                    try:
                        from docx import __version__ as version
                    except ImportError:
                        version = "unknown"
                
                if version is None:
                    print(f"Warning: Could not determine version for {package}")
                
                # For now, just note that it's installed
                print(f"✅ {package} is installed.")
                
            except ImportError:
                missing_packages.append(package)
                print(f"❌ {package} is not installed.")
        
        return len(missing_packages) == 0, missing_packages
    
    @staticmethod
    def install_dependencies(missing_packages):
        """
        Install missing dependencies
        Returns True if successful, False otherwise
        """
        if not missing_packages:
            return True
        
        print(f"\nAttempting to install {len(missing_packages)} missing packages...")
        
        # Determine pip command based on the platform
        pip_cmd = "pip"
        if platform.system() == "Windows":
            pip_cmd = f"{sys.executable} -m pip"
        
        for package in missing_packages:
            print(f"Installing {package}...")
            try:
                # Run pip install
                subprocess.check_call(f"{pip_cmd} install {package}", shell=True)
                print(f"✅ Successfully installed {package}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install {package}: {e}")
                return False
        
        return True

    @staticmethod
    def check_and_install():
        """
        Check dependencies and attempt to install missing ones
        Returns True if all dependencies are available (either pre-existing or successfully installed)
        """
        print("Checking system dependencies...")
        all_installed, missing_packages = DependencyChecker.check_dependencies()
        
        if all_installed:
            print("\nAll required dependencies are installed! ✅")
            return True
        
        # Ask user for permission to install
        response = input(f"\nWould you like to install the missing packages? (y/n): ")
        if response.lower() in ['y', 'yes']:
            success = DependencyChecker.install_dependencies(missing_packages)
            if success:
                print("\nAll dependencies have been installed successfully! ✅")
                return True
            else:
                print("\nSome dependencies could not be installed. Please install them manually. ❌")
                print("You can try running: pip install " + " ".join(missing_packages))
                return False
        else:
            print("\nPlease install the missing dependencies manually:")
            print("pip install " + " ".join(missing_packages))
            return False

