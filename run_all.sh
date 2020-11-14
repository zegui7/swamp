kill $(pgrep chromedriver | xargs)

for i in $(seq 1 $(($(python3 mapping_the_swamp.py list | wc -l)-1)))
do 
    function retry { python3 mapping_the_swamp.py $i && echo "success" || (echo "fail" && retry) }; retry
done
