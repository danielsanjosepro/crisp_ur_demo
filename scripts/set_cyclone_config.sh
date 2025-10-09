#!/bin/bash

export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export CYCLONEDDS_URI=file://$(pwd)/src/crisp_ur_demo/config/cyclonedds.xml
echo "CycloneDDS configuration set to: $CYCLONEDDS_URI"
