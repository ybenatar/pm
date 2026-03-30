#!/bin/bash
echo "Stopping pm_container..."
docker stop pm_container || true
echo "Removing pm_container..."
docker rm pm_container || true
echo "Done!"
