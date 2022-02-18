#!/bin/bash
i=${1:-5}

if [[ ! -v $2 ]];then
  if [[ -n $(docker ps -a -q) ]];then
   docker stop $(docker ps -a -q)
   docker rm $(docker ps -a -q)
  fi
fi


for (( ; i>0; i-- ));do
 setsid --fork st -e bash -c "bash runDocker.sh \"Worker\"$i$2 ; read"
done
