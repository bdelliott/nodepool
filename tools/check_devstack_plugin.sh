#!/bin/bash -x

# Do this so that the nodepool commands below can find the
# clouds.yaml file
export OS_CLIENT_CONFIG_FILE=${OS_CLIENT_CONFIG_FILE:-/opt/stack/new/.config/openstack/clouds.yaml}
NODEPOOL_CONFIG=${NODEPOOL_CONFIG:-/etc/nodepool/nodepool.yaml}
NODEPOOL="nodepool -c $NODEPOOL_CONFIG"

function waitforimage {
    name=$1
    state='ready'

    while ! $NODEPOOL image-list | grep $name | grep $state; do
        $NODEPOOL image-list > /tmp/.nodepool-image-list.txt
        $NODEPOOL list > /tmp/.nodepool-list.txt
        sudo mv /tmp/.nodepool-image-list.txt $WORKSPACE/logs/nodepool-image-list.txt
        sudo mv /tmp/.nodepool-list.txt $WORKSPACE/logs/nodepool-list.txt
        sleep 10
    done
}

function waitfornode {
    name=$1
    state='ready'

    while ! $NODEPOOL list | grep $name | grep $state; do
        $NODEPOOL image-list > /tmp/.nodepool-image-list.txt
        $NODEPOOL list > /tmp/.nodepool-list.txt
        sudo mv /tmp/.nodepool-image-list.txt $WORKSPACE/logs/nodepool-image-list.txt
        sudo mv /tmp/.nodepool-list.txt $WORKSPACE/logs/nodepool-list.txt
        sleep 10
    done
}

# Check that snapshot image built
waitforimage trusty-server
# check that dib image built
waitforimage ubuntu-dib

# check snapshot image was bootable
waitfornode trusty-server
# check dib image was bootable
waitfornode ubuntu-dib
