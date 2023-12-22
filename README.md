# GHE Miner
GitMiner will query Github useful source code data at the Enterprise, Organization or Repository level.

# Usage

The `entgitminer.py` is called as a CLI app. It can be run with your local python.
All output gets saved to the logs/ dir in the working directory

```
usage: entgitminer.py [-h] --hostname HOSTNAME [--org ORG_NAME] [--repo REPO_NAME] [-a]

optional arguments:
  -h, --help           show this help message and exit
  --hostname HOSTNAME  Hostname URL: acme
  --org ORG_NAME       Organization Name(ex: DevOps)
  --repo REPO_NAME     Repository Name(ex: GitMiner)
  -a, --all            To run in all orgs and repos, set this flag.
```

# Requirements
Python 3.6+

```
pip3 install -r requirements.txt
```

# Setup

All queries require authentication. You will NEED a Personal Token in the `config.json` file.

Make sure you do the following first:
 - Copy `config.json.example` to `config.json`
 - Update `config.json` with Github tokens

```
{
    "ACME_GITHUB_HOSTNAME": "github.ACME.co",
    "ACME_GITHUB_TOKEN": "{Your personal ACME Github Token}"
}
```

# Examples
Get a single repo from an org:

Local run:

```
$ python entgitminer.py --hostname acme --org DevOps --repo GitMiner
```


Get all repos for a single org:

```
$ python entgitminer.py --hostname acme --org DevOps
```

Get all repos for all orgs:

```
$ python entgitminer.py --hostname acme --all
```

# Sample Output

```
**************************************************
               ENTGITMINER:
A tool to mine useful data from Github Enterprise
**************************************************


[.] Are you sure you want to run this script in github.acme.co: (y/n)

y

[.] Using: github.acme.co

Organization: DevOps
Owner: John.Doe
Org Url: https://github.acme.co/DevOps
Repos:
 |
 |- Repo Name: Maestro
 |- Core Language: Java
 |- Languages:
  |
   |- Language: Java
   |- Byte Size: 3.1650390625 KB
  |
   |- Language: Kotlin
   |- Byte Size: 1.2666015625 KB
  |
   |- Language: Dockerfile
   |- Byte Size: 0.333984375 KB
 |- Root Content Files:
  |
   | * .gitattributes
   | * .gitignore
   | * .idea
   | * Dockerfile
   | * Jenkinsfile.norfolk
   | * README.md
   | * build.gradle.kts
   | * build.yaml
   | * docker-compose.debug.yml
   | * docker-compose.yml
   | * gradle
   | * gradlew
   | * gradlew.bat
   | * settings.gradle.kts
   | * src
 |
 |- Repo Name: example-test
 
 
 ...


**************************************
[*] Grand Total number of Orgs: 1
[*] Grand Total number of Repos: 84
**************************************
Language            Count  Percentage
----------------  -------  ------------
Python                 34  40%
Empty                  22  26%
Java                    8  9%
JavaScript              6  7%
HCL                     5  5%
HTML                    4  4%
Lua                     1  1%
Rich Text Format        1  1%
TypeScript              1  1%
Dockerfile              1  1%
SaltStack               1  1%

```
