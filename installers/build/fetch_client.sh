#!/bin/bash -xe

#Download and extract desktop client 
platform=$1

dest=/artifacts/build/dc/${platform}
if [  -d ${dest} ] ; then
    rm -rf ${dest}
fi

mkdir -p ${dest}
aws s3 cp s3://${AWS_S3_BUCKET_NAME}/conductor-desktop/conductor-desktop-latest-${platform}.zip ${dest}
unzip ${dest}/conductor-desktop-latest-${platform}.zip  -d ${dest}
rm -f ${dest}/conductor-desktop-latest-${platform}.zip