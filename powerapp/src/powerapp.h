#ifndef __POWERAPP_H__
#define __POWERAPP_H__


#include <stdlib.h>
#include <stdint.h>
#include <dirent.h>
#include <string.h>
#include <stdio.h>
#include <unistd.h>
#include <time.h>

// Parameters default
#define MIN_US			    10200L // 11ms
#define DEFAULT_US		    20000L // 20ms
#define DEFAULT_POWER       0
#define DEFAULT_RAW		    1
#define DEFAULT_OUTFILE	    "powerapp.csv"
#define DEFAULT_SAMPLES     100
#define DEFAULT_CONTINUOUS  0

// These are specific to ZCU102
// NOTE: these correspond to hwmonitors 2-19
#define VCCPSINTFP 0
#define VCCPSINTLP 1
#define VCCPSAUX 2
#define VCCPSPLL 3
#define MGTRAVCC 4
#define MGTRAVTT 5
#define VCCPSDDR 6
#define VCCOPS 7
#define VCCOPS3 8
#define VCCPSDDRPLL 9
#define VCCINT  10
#define VCCBRAM 11
#define VCCAUX 12
#define VCC1V2 13
#define VCC3V3 14
#define VADJ_FMC 15
#define MGTAVCC 16
#define MGTAVTT 17


const char railname_arr[50][12] = {
		"VCCPSINTFP",
		"VCCPSINTLP",
		"VCCPSAUX",
		"VCCPSPLL",
		"MGTRAVCC",
		"MGTRAVTT",
		"VCCPSDDR",
		"VCCOPS",
		"VCCOPS3",
		"VCCPSDDRPLL",
		"VCCINT",
		"VCCBRAM",
		"VCCAUX",
		"VCC1V2",
		"VCC3V3",
		"VADJ_FMC",
		"MGTAVCC",
		"MGTAVTT"
};

typedef struct ina226 {

	char current_path[50];
	char voltage_path[50];
	char name[12];
	unsigned int current;
	unsigned int voltage;

} ina226_t;

int cmp_ina226(const void *a, const void *b) {
	ina226_t *temp1 = (ina226_t*)a;
	ina226_t *temp2 = (ina226_t*)b;
	unsigned int len1 = strlen(temp1->current_path);
	unsigned int len2 = strlen(temp2->current_path);

	if (len1==len2){
		return strcmp(temp1->current_path, temp2->current_path);
	} else if (len1>len2){
		return 1;
	} else {
		return -1;
	}

}

void populate_ina226_array(ina226_t *ina226_list, size_t* ina226_list_size) {
	DIR *d;
	struct dirent *dir;

	char buffer[100];
	char fname_buff[100];

	FILE *fptr;

	d = opendir("/sys/class/hwmon/");
	unsigned int i = 0;

	while ((dir = readdir(d)) != NULL) {
		if (strncmp(".", dir->d_name, 1) == 0) {
			continue;
		}
		//printf("tree: %s\n", dir->d_name);
		strcpy(fname_buff, "/sys/class/hwmon/"); // links to  /sys/devices/platform/ina226-*
		strcat(fname_buff, dir->d_name);
		strcat(fname_buff, "/name");

		//printf("name: %s\n", fname_buff);

		fptr = fopen(fname_buff, "r");
		size_t fread_ret = fread(&buffer, 10, 1, fptr);
		//printf("device type: %s", buffer);

		if (strncmp(buffer, "ina226", 3) == 0) {
			fname_buff[strlen(fname_buff)-5] = 0;

			strcpy(ina226_list[i].current_path,fname_buff);
			strcat(ina226_list[i].current_path,"/curr1_input");

			strcpy(ina226_list[i].voltage_path,fname_buff);
			// strcat(ina226_list[i].voltage_path,"/in1_input"); // mostly zero
			strcat(ina226_list[i].voltage_path,"/in2_input");

//			printf("found: %s\n", ina226_list[i].ina226_dir);
			i++;
		}

	}

	qsort(ina226_list, i, sizeof(ina226_t), cmp_ina226);

	*ina226_list_size = i;
	for ( unsigned int i = 0; i < *ina226_list_size; i++) {
		sprintf(ina226_list[i].name, "%s", railname_arr[i]);
	}

	closedir(d);
}

void list_ina226_list (ina226_t *ina226_list, size_t ina226_list_size) {

	for ( unsigned int i = 0; i < ina226_list_size; i++) {
		printf("Found ina226 %02d at dir: %s, %s\n", i, ina226_list[i].current_path,  ina226_list[i].name);
	}

	// Expected output for zcu102
	// Found ina226 00 at dir: /sys/class/hwmon/hwmon2/curr1_input, VCCPSINTFP
	// Found ina226 01 at dir: /sys/class/hwmon/hwmon3/curr1_input, VCCPSINTLP
	// Found ina226 02 at dir: /sys/class/hwmon/hwmon4/curr1_input, VCCPSAUX
	// Found ina226 03 at dir: /sys/class/hwmon/hwmon5/curr1_input, VCCPSPLL
	// Found ina226 04 at dir: /sys/class/hwmon/hwmon6/curr1_input, MGTRAVCC
	// Found ina226 05 at dir: /sys/class/hwmon/hwmon7/curr1_input, MGTRAVTT
	// Found ina226 06 at dir: /sys/class/hwmon/hwmon8/curr1_input, VCCPSDDR
	// Found ina226 07 at dir: /sys/class/hwmon/hwmon9/curr1_input, VCCOPS
	// Found ina226 08 at dir: /sys/class/hwmon/hwmon10/curr1_input, VCCOPS3
	// Found ina226 09 at dir: /sys/class/hwmon/hwmon11/curr1_input, VCCPSDDRPLL
	// Found ina226 10 at dir: /sys/class/hwmon/hwmon12/curr1_input, VCCINT
	// Found ina226 11 at dir: /sys/class/hwmon/hwmon13/curr1_input, VCCBRAM
	// Found ina226 12 at dir: /sys/class/hwmon/hwmon14/curr1_input, VCCAUX
	// Found ina226 13 at dir: /sys/class/hwmon/hwmon15/curr1_input, VCC1V2
	// Found ina226 14 at dir: /sys/class/hwmon/hwmon16/curr1_input, VCC3V3
	// Found ina226 15 at dir: /sys/class/hwmon/hwmon17/curr1_input, VADJ_FMC
	// Found ina226 16 at dir: /sys/class/hwmon/hwmon18/curr1_input, MGTAVCC
	// Found ina226 17 at dir: /sys/class/hwmon/hwmon19/curr1_input, MGTAVTT

	printf(
		"hwmons 2-11 are on PS_PMBUS\n"
		"hwmons 12-19 are on PL_PMBUS\n"
		"PS  = VCCPSINTFP + VCCPSINTLP + VCCPSAUX + VCCPSPLL + VCCPSDDR + VCCOPS + VCCOPS3 + VCCPSDDRPL\n"
		"PL  = VCCINT + VCCBRAM + VCCAUX + VCC1V2VCC3V3\n"
		"MGT = MGTRAVCC + MGTRAVTT + MGTAVCC + MGTAVTT\n"
		"Total Power = PS + PL + MGT\n"
	);

	return;
}

#endif // __POWERAPP_H__