from setuptools import setup
from glob import glob
import os

package_name = "crisp_ur_demos"

setup(
    name=package_name,
    version="0.0.1",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*.py")),
        (os.path.join("share", package_name, "config"), glob("config/*.yaml")),
        (os.path.join("share", package_name, "config"), glob("config/*.xacro")),
        (os.path.join("share", package_name, "config"), glob("config/*.xml")),
        (os.path.join("share", package_name, "config"), glob("config/assets/*.obj")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="ros",
    maintainer_email="42489409+danielsanjosepro@users.noreply.github.com",
    description="CRISP Controllers demos for Universal Robots with effort interface",
    license="Apache-2.0",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [],
    },
)
