kill $(pgrep chromium-browse | xargs)

for i in $(seq 1 $(($(python3 mapping_the_swamp.py --idx list | wc -l)-1)))
do 
	DONE=0
	while [ $DONE == 0 ]
	do
		python3 mapping_the_swamp.py --idx $i && DONE=1
	done
done
