
#!/bin/sh


NSLMON="/usr/local/nsl/bin/nslmon"

${NSLMON} -u 0
${NSLMON} -u 1
${NSLMON} -u 2
${NSLMON} -u 3

${NSLMON} -u 0 --clrf --clrl --clrc
${NSLMON} -u 1 --clrf --clrl --clrc
${NSLMON} -u 2 --clrf --clrl --clrc
${NSLMON} -u 3 --clrf --clrl --clrc
