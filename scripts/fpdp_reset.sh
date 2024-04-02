
#!/bin/sh


NSLMON="/usr/local/nsl/bin/nslmon"

${NSLMON} -A

${NSLMON} -u 0 --clrf --clrl --clrc
${NSLMON} -u 1 --clrf --clrl --clrc
${NSLMON} -u 2 --clrf --clrl --clrc
${NSLMON} -u 3 --clrf --clrl --clrc
