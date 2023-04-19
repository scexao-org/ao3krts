/*
 * lib_track.c -- Functions for dealing with tracking mode
 *
 * Written by Yosuke Minowa (based on lib_track.c written by Oya-san) 
 */

#include <stdio.h>				/* for snprintf() */
#include <stdlib.h>				/* for strtod() */
#include <string.h>				/* for strspn(), memmove() */
#include <ctype.h>				/* for isdigit(), tolower() */
#include <errno.h>			/* for errno */
#include <math.h>
#include <time.h>                       /* for time_t */
#include "stringx.h"			/* for strtolower() */
#include "libtrack.h"

 
/****************************************************************************/
/* JulianDate                                                               */
/****************************************************************************
# Calculate Julian date for a specified calendar date
# (based on the equation in "2007 Japanese Ephemeris, p.438");
# [INPUT]
# - year:   year, the first line of the tracking file (scalar)
# - month:   month, the first line of the tracking file (scalar)
# - day:   day, the first line of the tracking file (scalar)
# [OUTPUT]
# - return:   Juliand date (scalar)
*/
static double JulianDate(int year, int month, int day){
  double JD;

  JD = fix( ( -fix((14-month)/12) + year + 4800) *1461/4 ) \
    + fix( ( fix((14-month)/12)*12 + month - 2) *367/12 ) \
    - fix( fix( (-fix((14-month)/12) + year + 4900) /100 ) *3/4 ) \
    + day - 32075.5;

  return(JD);
}

/****************************************************************************/
/* GMST0je2007                                                              */
/****************************************************************************
# Calculate Greenwich Mean Sidereal Time at 0hUT for a specified Julian date
# (based on the equation in "2007 Japanese Ephemeris, p.442");
# [INPUT]
# - JD:   Juliand date (scalar)
# [OUTPUT]
# - return:   GMST0 ([rad], scalar)
*/
static double GMST0je2007(double JD){
  double JC,GMST,GMr;

  /* Julian Century */
  JC = (JD-2451545.0)/36525;
  GMST = 24110.54841 + 8640184.812866*JC + 0.093104*JC*JC - 0.0000062*JC*JC*JC;   //[sec]; see Japanese Ephemeris

  GMr=(2*M_PI)*fmod(GMST/86400,1);   // fraction part of GSMT[s]; to delete overwrap by rotation of 24[h]=86400[s]

  return(GMr);
}

/****************************************************************************/
/* precession2000                                                           */
/****************************************************************************
# Conver RA,DEC coordinates at epoch J2000 to that of the day
# (based on the equation in "2007 Japanese Ephemeris, p.442");
# [INPUT]
# - JC:   Juliand date (=(JD - 2451545.0)/36525, scalar)
# - alpha0:   ([rad], RA of the coordinates, J2000)
# - delta0:   ([rad], DEC of the coordinates, J2000)
# [OUTPUT]
# - alpha:   ([rad], RA of the coordinates at the day)
# - delta:   ([rad], DEC of the coordinates at the day)
*/
static int precession2000(double JC, double alpha0, double delta0, double *alpha, double *delta){
  double M,N;
  double alpham,deltam;

  M = (M_PI/180)*(1.28115591*JC + 0.00038797*JC*JC + 0.00001005*JC*JC*JC + 0.04e-7*JC*JC*JC*JC);   // [rad]
  N = (M_PI/180)*(0.55671993*JC - 0.00011859*JC*JC - 0.00001162*JC*JC*JC - 0.2e-7*JC*JC*JC*JC);   // [rad]

  /***** Coordinate at J2000.0 *****/
  /* mean value */
  alpham = alpha0 + 0.5*(M+N*sin(alpha0)*tan(delta0));
  deltam = delta0 + 0.5*N*cos(alpham);

  /* Conver to the epoch of the day */
  *alpha = alpha0 + M + N*sin(alpham)*tan(deltam);
  *delta = delta0 + N*cos(alpham);

  return 0;
}

/* 
 * extract string at the specified range in the input string 
 * and convert it to integer format.
 */
int substr_int(char *str, int start, int length, int *val, int min, int max){
  char outstr[length+1];
  char *s;
  long l;

  if(strlen(str) < start + length){
    return -1;
  }

  strncpy(outstr, str+start, length);
  outstr[length] = '\0';

  errno = 0;
  l = strtol(outstr, &s, 10);
  if(errno || *s != '\0' || ((min != 0 || max !=0) && (l < min || l > max))){
    return -1;
  }

  *val = l;
    
  return 0;
}

/* 
 * extract string at the specified range in the input string 
 * and convert it to double format.
 */
int substr_dbl(char *str, int start, int length, double *val, double min, double max){
  char outstr[length+1];
  char *s;
  double d;

  if(strlen(str) < start + length){
    return -1;
  }

  strncpy(outstr, str+start, length);
  outstr[length] = '\0';

  errno = 0;
  d = strtod(outstr, &s);
  if(errno || *s != '\0' || ((min != 0 || max !=0) && (d < min || d > max))){
    return -1;
  }

  *val = d;
    
  return 0;
}

/* Resolve RA coordinate (HH:MM:SS.SSS) and convert it to radian */
int resolve_ra(char *ra, double *alpha){
  int argc;
  char *argv[3];
  double rah, ram, ras;
  char *s;

  argc = strsplit_delim(ra, argv,":", 3);

  if(argc == 3){
    errno = 0;
    rah = strtod(argv[0],&s);
    if(errno || *s != '\0' || (rah < 0.0 || rah >= 24.0)){
      return -1;
    }
    
    errno = 0;
    ram = strtod(argv[1],&s);
    if(errno || *s != '\0' || (ram < 0.0 || ram >= 60.0)){
      return -1;
    }
    
    errno = 0;
    ras = strtod(argv[2],&s);
    if(errno || *s != '\0' || (ras < 0.0 || ras >= 60.0)){
      return -1;
    }
    
  }else if(argc == 1){
    if(substr_dbl(ra, 0, 2, &rah, 0, 23) < 0 || 
       substr_dbl(ra, 2, 2, &ram, 0, 59) < 0 || 
       substr_dbl(ra, 4, strlen(ra)-4, &ras, 0, 60) < 0)
      return -1;
  }else{
    return -1;
  }

  /* convert to radian */
  *alpha = (M_PI/180.0) * 15.0 * (rah + ram / 60.0 + ras / 3600.0);

  return 0;
}

/* Resolve Dec coordinate (DD:MM:SS.SS) and convert it to radian */
int resolve_dec(char *dec, double *delta){
  int argc;
  char *argv[3];
  double decd, decm, decs;
  char *s;
  int sign=1,start=0;
  char csign[2];

  argc = strsplit_delim(dec, argv,":", 3);
  if(argc == 3){
    errno = 0;
    decd = strtod(argv[0],&s);
    if(errno || *s != '\0' || (decd < -90.0 || decd > 90.0)){
      return -1;
    }
    
    /* check sign of the declination */
    if(strstr(argv[0],"-") != NULL){
      sign = -1;
    }else{
      sign = 1;
    }
    
    errno = 0;
    decm = strtod(argv[1],&s);
    if(errno || *s != '\0' || (decm < 0.0 || decm >= 60.0)){
      return -1;
    }
    
    errno = 0;
    decs = strtod(argv[2],&s);
    if(errno || *s != '\0' || (decs < 0.0 || decs >= 60.0)){
      return -1;
    }
    
  }else if(argc == 1){
    if(strlen(dec) > 0){
      strncpy(csign, dec, 1);
      csign[1] = '\0';
      if(strcmp(csign,"+") == 0){
	start = 1;
	sign = 1;
      }else if (strcmp(csign,"-") == 0){
	start = 1;
	sign = -1;
      }else{
	start = 0;
	sign = 1;
      }
    }else{
      return -1;
    }
      
    if(start == 1){
      if (substr_dbl(dec, 0, 3, &decd, -90, 90) < 0 || 
	  substr_dbl(dec, 3, 2, &decm, 0, 59) < 0 || 
	  substr_dbl(dec, 5, strlen(dec)-5, &decs, 0, 60) < 0)
	return -1;
    }else{
      if (substr_dbl(dec, 0, 2, &decd, -90, 90) < 0 || 
	  substr_dbl(dec, 2, 2, &decm, 0, 59) < 0 || 
	  substr_dbl(dec, 4, strlen(dec)-4, &decs, 0, 60) < 0)
	return -1;
    }
  }else{
    return -1;
  }
  
  /* convert to radian */
  if(sign < 0){
    *delta = (M_PI/180.0) * (decd - decm / 60.0 - decs / 3600.0);
  }else{
    *delta = (M_PI/180.0) * (decd + decm / 60.0 + decs / 3600.0);
  }
  
  return 0;
}

/* Resolve UTC in the format of YYYYMMDDHHMMSS[.SSS] and convert it to unix time */
int resolve_utc(char *utc, time_t *t){
  int ret;
  struct tm time;

  if(utc == NULL){
    return -1;
  }

  if((ret = substr_int(utc,0,4,&(time.tm_year),2000,2037)) < 0){
    return ret;
  }
  time.tm_year = time.tm_year - 1900;

  if((ret = substr_int(utc,4,2,&(time.tm_mon),1,12)) < 0){
    return ret;
  }
  time.tm_mon = time.tm_mon - 1;

  if((ret = substr_int(utc,6,2,&(time.tm_mday),1,31)) < 0){
    return ret;
  }

  if((ret = substr_int(utc,8,2,&(time.tm_hour),0,23)) < 0){
    return ret;
  }

  if((ret = substr_int(utc,10,2,&(time.tm_min),0,59)) < 0){
    return ret;
  }

  if((ret = substr_int(utc,12,2,&(time.tm_sec),0,59)) < 0){
    return ret;
  }
  
  *t = timegm(&time);

  return 0;
}

/* 
 *  Calculate telescope Az/El in radian from RA2000 and Dec2000 in radian
 */
int get_current_azel(double alpha0, double delta0, double *az, double *el){
  time_t timer;
  struct tm *date;
  int year, month, day;
  int Uh, Um, Us;
  double JD,JC;
  double gmst0r,Ur0;
  double alpha,delta;
  double gstr, ha, lst;
  double CP,CH,CD,SP,SH,SD;
  double xh,yh,zh;

  /* get current date and time in UTC */
  time(&timer);
  date = gmtime(&timer);
  year = date->tm_year + 1900;
  month = date->tm_mon + 1;
  day = date->tm_mday;
  Uh = date->tm_hour;
  Um = date->tm_min;
  Us = date->tm_sec;

  /* Julian Date */
  JD = JulianDate(year,month,day);
  JC = (JD - 2451545.0)/36525;
  
  /* Greenwich Mean Sidereal Time at 0hUT */
  gmst0r = GMST0je2007(JD);

  /* Universal time */
  Ur0 = (M_PI/43200.0)*( (double)(3600*Uh + 60*Um + Us) ); // [s] -> [rad]

  /* coordinate of the dat */
  precession2000(JC,alpha0,delta0,&alpha,&delta);

  /*** Greenwitch mean sidereal time ***/
  /* (siderela/solar; "Astronomical Alumanac 2008, B8") */
  gstr = gmst0r + Ur0*1.00273790935;  // [rad]
  /*** local mean sidereal time ***/
  /* (note that the east longitude is defined as '+') */
  lst = gstr + L_RAD;   // [rad]
  /*** hour angle ***/
  ha = lst - alpha;   // [rad]

  /******** Coordinates conversion *******/
  /*** sine and cosine of angles ***/
  CP = cos(P_RAD); SP = sin(P_RAD);   // latitude
  CH = cos(ha); SH = sin(ha);   // hour angle
  CD = cos(delta); SD = sin(delta);   // declination

  /*** conversion ***/
  xh = SP*CH*CD - CP*SD;
  yh = -SH*CD;
  zh = CP*CH*CD + SP*SD;

  /* AZ [radian] */
  //*az = pi - atan2(yh,xh); // 0 < alpha < 2pi; (0=North)
  *az = - atan2(yh,xh); // -pi < alpha < pi; (0=South; Subaru)
   
  /* EL [radian] */
  *el = atan2(zh,sqrt(xh*xh+yh*yh));
   
  return 0;
}


/* 
 * Differential atmospheric dispersion
 * Original source is drawn from the IDL code "diff_atm_refr.pro"
 * obtained from ESO web page. 
 * http://www.eso.org/gen-fac/pubs/astclim/lasilla/diffrefr.html
 * === Prameters ===
 * el: telescope elevation in radian
 * lambda: observing wavelenght in micron
 * lambda0: reference wavelength in micron 
 * TC: temperature in degC
 * RH: relative humidiry in %
 * P:  pressure in mbar
 * === Output ===
 * dr: The Differential Atmospheric Dispersion in arcseconds
 *     with respect to the reference wavelength.
 */
double dar(double el, double lambda, double lambda0, double TC, double RH, double P){
  double z;
  double T;
  double PS,P1,P2;
  double D1,D2;
  double S0,S;
  double N0_1, N_1;
  double DR;

  // zenith distance 
  z = 0.5*M_PI - el;
  // temperature in kelvin
  T = TC + 273.15;
  
  PS = -10474.0 + 116.43*T - 0.43284*T*T + 0.00053840*T*T*T;
  P2 = RH / 100.0*PS;
  P1 = P - P2;
  
  D1 = P1 / T*(1.0+P1*(57.90*1.0E-8-(9.3250*1.0E-4/T)+(0.25844/pow(T,2))));
  D2 = P2 / T*(1.0+P2*(1.0+3.7E-4*P2)*(-2.37321E-3+(2.23366/T)-(710.792/pow(T,2))+(7.75141E4/pow(T,3))));

  S0=1.0/lambda0;
  S=1.0/lambda;

  N0_1 = 1.0E-8*((2371.34+683939.7/(130-pow(S0,2))+4547.3/(38.9-pow(S0,2)))*D1 + (6487.31+58.058*pow(S0,2)-0.71150*pow(S0,4)+0.08851*pow(S0,6))*D2);
  N_1 = 1.0E-8*((2371.34+683939.7/(130-pow(S,2))+4547.3/(38.9-pow(S,2)))*D1+ (6487.31+58.058*pow(S,2)-0.71150*pow(S,4)+0.08851*pow(S,6))*D2);

  // differential atmospheric dispersion in arcsec
  DR=tan(z)*(N0_1-N_1)*206264.8;

  return DR;

}

/* calculate Parallactic Angle from Az, EL in radian */
double tp(double az, double el){
  return atan2(sin(az),sin(el)*cos(az)+cos(el)*tan(P_RAD));
}


/* 
 *  Calculate PAD in case of the ADI mode 
 */
double calc_adipa(double alpha0, double delta0, double offset){
  double az, el;
  double pa;

  /* get current Az, EL */
  get_current_azel(alpha0, delta0, &az, &el);

  pa = tp(az,el) + ADI_OFFSET * (M_PI/180.0) + offset; 
  
  return pa;
}
