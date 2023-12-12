/**
 * @brief powerapp demo
 * 
 * Copyright:
 * 	Author(s) of https://github.com/jparkerh/xilinx-linux-power-utility/
 * 	Author(s) of https://www.xilinx.com/developer/articles/accurate-design-power-measurement.html
 *  Vincenzo Maisto <vincenzo.maisto2@unina.it>
 * 
 */

#include "powerapp.h"

int run_bm ( 
				char power_filename[50],
				unsigned long sampling_period_us,
				unsigned int raw,
				unsigned int power,
				unsigned int iterations,
				unsigned int continuous,
				ina226_t *ina226_list,
				size_t ina226_list_size
			) {
	FILE *power_fd;
	FILE *raw_currents_fd;
	FILE *raw_voltages_fd;
	FILE *ina226_fd;
	char raw_filename[128];
	char buffer[20];

	// Computed power
	float pl_power_mW = 0;
	float ps_power_mW = 0;
	float mgt_power_mW = 0;
	float total_power_mW = 0;

	// start and end timestamps
	struct timespec end_measure;
	struct timespec start_measure;

	// Open output files and print headers
	// Open output files and print headers
	if ( power == 1 ) {
		power_fd = fopen(power_filename, "w");
		if ( power_fd == NULL ) {
			fprintf(stderr, "Can't open %s\n", power_filename);
			return -1;
		}
		fprintf(power_fd, "Sample;PS mW;PL mW;MGT mW;Total mW\n");
	}
	// Raw data files
	if ( raw == 1 ) {
		// Currents
		strcpy(raw_filename, power_filename);
		strcat(raw_filename, ".raw_currents");
		raw_currents_fd = fopen(raw_filename, "w");
		if ( raw_currents_fd == NULL ) {
			fprintf(stderr, "Can't open %s\n", raw_filename);
			return -1;
		}

		// Print header
		fprintf(raw_currents_fd, "Sample; Timestamp");
		for ( unsigned int i = 0; i < ina226_list_size; i++) {
			fprintf(raw_currents_fd, "%s mA", ina226_list[i].name);
			if ( i != (ina226_list_size -1) ) {
				fprintf(raw_currents_fd, ";");
			}
		}
		fprintf(raw_currents_fd, "\n");

		// Voltages
		strcpy(raw_filename, power_filename);
		strcat(raw_filename, ".raw_voltages");
		raw_voltages_fd = fopen(raw_filename, "w");
		if ( raw_voltages_fd == NULL ) {
			fprintf(stderr, "Can't open %s\n", raw_filename);
			return -1;
		}

		// Print header
		fprintf(raw_voltages_fd, "Sample;");
		for ( unsigned int i = 0; i < ina226_list_size; i++) {
			fprintf(raw_voltages_fd, "%s mV", ina226_list[i].name);
			if ( i != (ina226_list_size -1) ) {
				fprintf(raw_voltages_fd, ";");
			}
		}
		fprintf(raw_voltages_fd, "\n");
	}

	// Collect samples
	for ( unsigned int j = 0; (j < iterations) | (continuous == 1); j++ ) {
		if ( raw == 1 ) {
			fprintf(raw_currents_fd, "%u;", j);
			fprintf(raw_voltages_fd, "%u;", j);
		}

		// Start measure on ina226 array
		clock_gettime(CLOCK_REALTIME, &start_measure);
		
		fprintf(raw_voltages_fd, "%s", buffer);
		fprintf(raw_currents_fd, "%s", buffer);

		for ( unsigned int i = 0; i < ina226_list_size; i++) {
			// Read voltage
			ina226_fd = fopen(ina226_list[i].voltage_path, "r");
			fscanf(ina226_fd,"%[^\n]", buffer);
			fclose(ina226_fd);

			ina226_list[i].voltage = atoi(buffer);

			if ( raw == 1 ) {
				fprintf(raw_voltages_fd, "%s", buffer);
				if ( i != (ina226_list_size -1) ) {
					fprintf(raw_voltages_fd, ";");
				}
			}

			// Read current
			ina226_fd = fopen(ina226_list[i].current_path, "r");
			fscanf(ina226_fd,"%[^\n]", buffer);
			fclose(ina226_fd);

			ina226_list[i].current = atoi(buffer);
			if ( raw == 1 ) {
				fprintf(raw_currents_fd, "%s", buffer);
				if ( i != (ina226_list_size -1) ) {
					fprintf(raw_currents_fd, ";");
				}
			}
		}
		if ( raw == 1 ){
			fprintf(raw_currents_fd, "\n");
			fprintf(raw_voltages_fd, "\n");
		}

		// Compute power
		if ( power == 1 ) {
			ps_power_mW = (float) (
						( ina226_list[VCCPSINTFP].voltage	*	ina226_list[VCCPSINTFP].current	 ) +
						( ina226_list[VCCPSINTLP].voltage	*	ina226_list[VCCPSINTLP].current	 ) +
						( ina226_list[VCCPSAUX].voltage	 	*	ina226_list[VCCPSAUX].current	 ) +
						( ina226_list[VCCPSPLL].voltage	 	*	ina226_list[VCCPSPLL].current	 ) +
						( ina226_list[VCCPSDDR].voltage	 	*	ina226_list[VCCPSDDR].current	 ) +
						// ( ina226_list[VCCOPS].voltage	 	*	ina226_list[VCCOPS].current		 ) + // curr1_input always = -9 on ZCU102
						// ( ina226_list[VCCOPS3].voltage	 	*	ina226_list[VCCOPS3].current	 ) + // curr1_input always = -9 on ZCU102
						( ina226_list[VCCPSDDRPLL].voltage	*	ina226_list[VCCPSDDRPLL].current )
					) / 1000.0;

			pl_power_mW = (float) (
						( ina226_list[VCCINT].voltage	*	ina226_list[VCCINT].current  ) +
						( ina226_list[VCCBRAM].voltage	*	ina226_list[VCCBRAM].current ) +
						( ina226_list[VCCAUX].voltage	*	ina226_list[VCCAUX].current  ) +
						( ina226_list[VCC1V2].voltage	*	ina226_list[VCC1V2].current  ) +
						( ina226_list[VCC3V3].voltage	*	ina226_list[VCC3V3].current  )
					) / 1000.0;

			mgt_power_mW = (float) (
						( ina226_list[MGTRAVCC].voltage	*	ina226_list[MGTRAVCC].current	) +
						( ina226_list[MGTRAVTT].voltage	*	ina226_list[MGTRAVTT].current	) +
						( ina226_list[MGTAVCC].voltage	*	ina226_list[MGTAVCC].current	) +
						( ina226_list[MGTAVTT].voltage	*	ina226_list[MGTAVTT].current	) +
						( ina226_list[VCC3V3].voltage	*	ina226_list[VCC3V3].current		)  
					) / 1000.0;

			total_power_mW =  mgt_power_mW + pl_power_mW + ps_power_mW;

			fprintf(power_fd, "%u;%.6f;%.6f;%.6f;%.6f\n", j, ps_power_mW, pl_power_mW, mgt_power_mW, total_power_mW);
		}

		// Wait before next sampling
		clock_gettime(CLOCK_REALTIME, &end_measure);

		double measure_latency_us = (double)(end_measure.tv_sec  - start_measure.tv_sec) * 1.0e6 + // sec to usec
							(double)(end_measure.tv_nsec - start_measure.tv_nsec) / 1.0e3; // nanosec to usec
		unsigned long usleep_us = sampling_period_us - (unsigned long)measure_latency_us;
		// printf("measure_latency_us %lu us\n", (unsigned long)measure_latency_us);
		// printf("sampling_period_us %lu us\n", sampling_period_us);
		// printf("waiting for %lu us\n", usleep_us);
		usleep( usleep_us );
	}

	// Close files
	if ( power == 1 ) {
		fclose(power_fd);
	}
	if ( raw == 1 ) {
		fclose(raw_currents_fd);
		fclose(raw_voltages_fd);
	}
}

void usage() {
	printf("./powerapp [FLAGS]"
			"\t -t Sampling interval in us	(default=%lu), not really real-time though\n"
			"\t -p Compute power			(default=%u), enable power computation\n"
			"\t -o Output power file		(default=%s), raw data files for voltages and currents\n"
			"\t -r Raw mode					(default=%u), save also raw measures (mV and mA)\n"
			"\t -n Number of samples		(default=%u)\n"
			"\t -d Continuous mode on		(default=%u), run indefinetly, overrides -n\n"
			"\t -l List discoverable ina226 and exit\n",
			DEFAULT_US,
			DEFAULT_POWER,
			DEFAULT_OUTFILE,
			DEFAULT_RAW,
			DEFAULT_SAMPLES,
			DEFAULT_CONTINUOUS
	);
}

unsigned int main(unsigned int argc, char *argv[]) {

	ina226_t ina226_list[30];
	size_t ina226_list_size;
	populate_ina226_array(ina226_list, &ina226_list_size);

	unsigned int opt;
	unsigned long sampling_period_us = DEFAULT_US;
	unsigned int raw = DEFAULT_RAW;
	unsigned int power = DEFAULT_POWER;
	unsigned int iterations = DEFAULT_SAMPLES;
	unsigned int continuous = DEFAULT_CONTINUOUS;
	char power_filename[50] = DEFAULT_OUTFILE;

	while ((opt = getopt(argc, argv, "r:p:t:o:n:l:c:h")) != -1) {
		switch (opt) {
			case 'r':
				raw = atoi(optarg);
				break;
			case 'p':
				power = atoi(optarg);
				break;
			case 't':
				sampling_period_us = strtoul(optarg, NULL, 0);
				if ( sampling_period_us < MIN_US ) {
					fprintf(stderr, "[ERROR] Sampling period must be greater that %lu us\n", MIN_US);
					return -1;
				}
				break;
			case 'o':
				strcpy(power_filename, optarg);
				break;
			case 'l':
				list_ina226_list(ina226_list, ina226_list_size);
				return 0;
			case 'n':
				iterations = atoi(optarg);
				break;
			case 'c':
				continuous = atoi(optarg);
				break;
			case 'h':
				usage();
				return 0;
		}
	}

	int ret_val = 0;
	ret_val = run_bm ( power_filename, 
						sampling_period_us,
						raw,
						power,
						iterations,
						continuous,
						ina226_list,
						ina226_list_size
					);		

	return ret_val;
}

