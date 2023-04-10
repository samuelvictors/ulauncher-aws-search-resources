const fs = require('fs')
const path = require('path');
const { execSync } = require('child_process')

const resourceFilePath = path.resolve(__dirname, 'resources.json')

const resourceList = [
  {
    'name': 'bucket',
    'command': "aws s3api list-buckets --query 'Buckets[*].Name'"
  },
  {
    'name': 'function',
    'command': "aws lambda list-functions --query 'Functions[*].FunctionName'"
  },
  {
    'name': 'table',
    'command': "aws dynamodb list-tables --query 'TableNames[]'"
  }
]

const readResourceFile = () => JSON.parse(fs.readFileSync(resourceFilePath))

const writeResourceFile = (data) => fs.writeFileSync(resourceFilePath, JSON.stringify(data, undefined, 2))

const getAwsResource = (command) => JSON.parse(execSync(command, { maxBuffer: 1024 * 1024 * 16 }).toString())

const process = ({ name, command }) => {
  console.log(`updating ${name}`)
  const resources = readResourceFile()
  const resourceNameList = getAwsResource(command)
  resources[name] = {}
  for (const resourceName of resourceNameList) {
    const match = resourceName.match(/-(beta|sdbx|prod|dvdv\w+)/)
    if (match) {
      const env = match[1]
      if (!resources[name][env]) {
        resources[name][env] = []
      }
      resources[name][env].push(resourceName)
    }
  }
  writeResourceFile(resources)
}

const exec = () => {
  for (const resourceItem of resourceList) {
    try {
      process(resourceItem)
    } catch (error) {
      console.log(`An error occurred while updating the ${resourceItem.name}.`, error)
    }
  }
}

exec()
