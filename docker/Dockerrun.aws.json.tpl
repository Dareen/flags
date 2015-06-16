{
  "AWSEBDockerrunVersion": "1",
  "Image": {
    "Name": "{{ IMAGE_NAME }}:{{ IMAGE_VERSION }}",
    "Update": "true"
  },
  "Authentication": {
      "Bucket": "dbz-build-deps",
      "Key": "generic/docker/.dockercfg"
  },
  "Ports": [
    {
      "ContainerPort": "80"
    }
  ],
  "Logging": "/var/log/dubizzle/"
}
