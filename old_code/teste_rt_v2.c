/*
 * Programa de Teste do Desempenho de Tempo Real com uso do Driver NIDAQmx
 *
 */
// Para compilar:
// gcc teste_rt_v2.c /usr/lib/x86_64-linux-gnu/libnidaqmx.so.22.8.0 -pthread -lm -lgsl -lgslcblas -o teste_rt
// Executar como superusuário

// Para acompanhar os processos e suas prioridades pelo terminal:
// ps -eLo pid,class,rtprio,ni,comm | grep -i "pid_app"
// Para acompanhar interrupções relevantes (nipalk para o driver,rtc0 para o relógio):
// ps -eLo pid,class,rtprio,ni,comm | grep -i "irq"
// Para mudar prioridade das interrupções:
// chrt -f -p 90 pid #onde pid é o process id

#include <limits.h>
#include <pthread.h>
#include <sched.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <errno.h>
#include <NIDAQmx.h>
#include <sys/resource.h>
#include <math.h>
#include <string.h>
#include <gsl/gsl_statistics_double.h>

#define NSEC_TO_SEC 1000000000
#define SAMPLING_TIME 400000 // ns
#define AMOSTRAS 10000
#define SAMPLES_PER_SECOND (1.0 * NSEC_TO_SEC / SAMPLING_TIME)
#define RT_PRIORITY 90

#define DAQmxErrChk(functionCall)            \
	if (DAQmxFailed(error = (functionCall))) \
		goto Error;                          \
	else

// Variáveis da placa de aquisição
int32 error = 0;
char errBuff[2048] = {'\0'};
TaskHandle AItaskHandle = 0;
TaskHandle AOtaskHandle = 0;

long cicloInicio[AMOSTRAS];
long cicloFim[AMOSTRAS];
double Diffs[AMOSTRAS - 1];
double workvec[AMOSTRAS - 1];
unsigned int count = 0;

int continua = 1;

struct period_info
{
	struct timespec next_period;
	long period_ns;
};

static void inc_period(struct period_info *pinfo)
{
	pinfo->next_period.tv_nsec += pinfo->period_ns;

	while (pinfo->next_period.tv_nsec >= 1000000000)
	{
		/* timespec nsec overflow */
		pinfo->next_period.tv_sec++;
		pinfo->next_period.tv_nsec -= 1000000000;
	}
}

static void periodic_task_init(struct period_info *pinfo)
{
	/* for simplicity, hardcoding a 1ms period */
	pinfo->period_ns = SAMPLING_TIME;

	clock_gettime(CLOCK_MONOTONIC, &(pinfo->next_period));
}

static void do_rt_task()
{
	/* Do RT stuff here. */
	int i;
	float64 data;

	// DAQmx Read Code
	//	printf("=%d",count);

	DAQmxErrChk(DAQmxReadAnalogScalarF64(AItaskHandle, 10.0, &data, NULL));
	// printf("data=%f",data);
	// Writing is much slower than reading!
	DAQmxErrChk(DAQmxWriteAnalogScalarF64(AOtaskHandle, 1, 0.0, 0.5 * data, NULL));
Out:
	return;
Error:
	if (DAQmxFailed(error))
		DAQmxGetExtendedErrorInfo(errBuff, 2048);
	if (DAQmxFailed(error))
		printf("DAQmx ErrorRead: %s\n", errBuff);
	return;
}

static void wait_rest_of_period(struct period_info *pinfo)
{
	int islate;

	//       inc_period(pinfo);
	/* for simplicity, ignoring possibilities of signal wakes */
	//       clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &pinfo->next_period, NULL);
	// what about sample complete event???
	DAQmxWaitForNextSampleClock(AItaskHandle, 15.0, &islate);
}

void *Thread_Carga_Processamento()
{
	double mediana;
	// double delta[AMOSTRAS-1];
	int j;

	printf("Inicio Thread_Carga_Processamento\n");
	while (continua)
	{
		pow(2, exp(5));
		// for(j=0;j<AMOSTRAS-1;j++){
		//	delta[j]=cicloInicio[j+1]-1.0*cicloInicio[j];
		//}
		//   mediana=gsl_stats_median(delta,1,AMOSTRAS-1);
	}
	printf("Fim Thread_Carga_Processamento\n");
	return 0;
} // Thread_Carga_Processamento

void *Thread_Carga_Arquivo()
{
	int i = 0;
	// Arquivo:
	FILE *ArqDados;
	printf("Inicio Thread_Carga_Arquivo\n");
	while (continua)
	{
		ArqDados = fopen("Carga.txt", "a+");
		if (ArqDados == NULL)
		{
			printf("\n  Erro ao Criar Arquivo Carga");
			printf("\n  Significado:%s \n", strerror(errno));
		}
		i = 0;
		for (i = 0; i < AMOSTRAS / 100; i++)
		{
			fprintf(ArqDados, "Leitura Escrita ModoOperacao ValorDesejado CicloInicio CicloFim, %d\n", i);
			fflush(ArqDados);
		}
		fclose(ArqDados);
	}
	printf("Fim Thread_Carga_Arquivo\n");
	return 0;
} //  Thread_Carga_Arquivo

void *simple_cyclic_task(void *data)
{
	struct period_info pinfo;
	struct timespec tempo;
	struct timespec tempo2;
	int j;
	struct rlimit rlim;
	double media = 0;
	double momento = 0;
	double AvgLatency = 0;
	int ret;

	//	getrlimit(RLIMIT_RTPRIO,&rlim);
	//	printf("prio_cur=%lu",rlim.rlim_cur);
	//	printf("prio_max=%lu",rlim.rlim_max);
	ret = sched_getscheduler(0);
	printf("priority=%d\n", ret);

	FILE *ArqTime;
	ArqTime = fopen("Tempo.txt", "a+");
	if (ArqTime == NULL)
	{
		printf("\n  Erro ao Criar Arquivo Tempo");
		// printf("\n  Significado: %s \n", strerror( errno));
	}

	periodic_task_init(&pinfo);
	while (count < AMOSTRAS)
	{
		ret = clock_gettime(CLOCK_MONOTONIC, &tempo);
		do_rt_task();
		cicloInicio[count] = tempo.tv_sec * 1000000 + tempo.tv_nsec / 1000; // tempo em usec
		ret = clock_gettime(CLOCK_MONOTONIC, &tempo2);
		//                cicloFim[count]=tempo2.tv_sec*1000000+tempo2.tv_nsec/1000; //tempo em usec
		wait_rest_of_period(&pinfo);
		cicloFim[count] = (tempo2.tv_sec - tempo.tv_sec) * 1000000 + (tempo2.tv_nsec - tempo.tv_nsec) / 1000; // tempo em usec
		count++;
	}
	for (j = 0; j < AMOSTRAS; j++)
	{
		fprintf(ArqTime, "%ld %ld\n", cicloInicio[j], cicloFim[j]);
		//             printf("%ld %ld\n", cicloInicio[j],cicloFim[j]);
		fflush(ArqTime);
		if (j >= 2)
		{
			momento += pow(cicloInicio[j] - 1.0 * cicloInicio[j - 1], 2);
			media += cicloInicio[j] - 1.0 * cicloInicio[j - 1];
			AvgLatency += cicloFim[j];
		}
	}
	fclose(ArqTime);
	media = media / (AMOSTRAS - 1);
	AvgLatency = AvgLatency / (AMOSTRAS - 1);
	momento = momento / (AMOSTRAS - 1);
	printf("media=%f\t", media);
	momento = sqrt(momento - pow(media, 2));
	printf("desvio=%f\t", momento);
	printf("latencia_media=%f\n", AvgLatency);
	for (j = 0; j < AMOSTRAS - 1; j++)
	{
		Diffs[j] = cicloInicio[j + 1] - 1.0 * cicloInicio[j];
		workvec[j] = cicloFim[j];
	}
	AvgLatency = gsl_stats_median(workvec, 1, AMOSTRAS - 1);
	printf("latencia_mediana=%f\n", AvgLatency);
	media = gsl_stats_median(Diffs, 1, AMOSTRAS - 1);
	printf("Mediana=%f\t", media);
	media = gsl_stats_mad(Diffs, 1, AMOSTRAS - 1, workvec);
	printf("MAD=%f\n", media);

	return NULL;
}

// Função para inicializar driver da placa de aquisição
static int Inicializa_placa(void)
{

	DAQmxErrChk(DAQmxCreateTask("", &AItaskHandle)); // cria tarefa de entrada analógica
	DAQmxErrChk(DAQmxCreateTask("", &AOtaskHandle)); // cria tarefa de saída analógica

	// configura canal de entrada
	DAQmxErrChk(DAQmxCreateAIVoltageChan(AItaskHandle, "Dev1/ai0", "", DAQmx_Val_Cfg_Default, -10.0, 10.0, DAQmx_Val_Volts, NULL));
	// configura canal de saída
	DAQmxErrChk(DAQmxCreateAOVoltageChan(AOtaskHandle, "Dev1/ao0", "", -10.0, 10.0, DAQmx_Val_Volts, NULL));

	// configura timers para tarefas de leitura e escrita
	DAQmxErrChk(DAQmxCfgSampClkTiming(AItaskHandle, "", SAMPLES_PER_SECOND, DAQmx_Val_Rising, DAQmx_Val_HWTimedSinglePoint, 1)); // DAQmx_Val_ContSamps or DAQmx_Val_HWTimedSinglePoint
	DAQmxErrChk(DAQmxCfgSampClkTiming(AOtaskHandle, "", SAMPLES_PER_SECOND, DAQmx_Val_Rising, DAQmx_Val_HWTimedSinglePoint, 1)); // DAQmx_Val_HWTimedSinglePoint or DAQmx_Val_ContSamps

	DAQmxSetRealTimeWaitForNextSampClkWaitMode(AItaskHandle, DAQmx_Val_WaitForInterrupt); // permitirá que a thread de tempo real durma enquanto aguarda o próximo interrupt
	DAQmxSetRealTimeConvLateErrorsToWarnings(AItaskHandle, 1);
	// evita que tarefa durma enquanto aguarda a leitura, o que poderia ceder o controle para um processo de menor prioridade
	DAQmxSetReadWaitMode(AItaskHandle, DAQmx_Val_Poll);

	// Inicia tarefas
	DAQmxErrChk(DAQmxStartTask(AItaskHandle));
	DAQmxErrChk(DAQmxStartTask(AOtaskHandle));

out:
	return 0;

Error:
	if (DAQmxFailed(error))
		DAQmxGetExtendedErrorInfo(errBuff, 2048);
	if (AItaskHandle != 0)
	{
		DAQmxStopTask(AItaskHandle);
		DAQmxClearTask(AItaskHandle);
	}
	if (DAQmxFailed(error))
		printf("DAQmx Error: %s\n", errBuff);
	return 0;
}

int main()
{
	struct sched_param param;
	pthread_attr_t attr, attr2;
	pthread_t thread;
	pthread_t threadProcessamento;
	pthread_t threadArquivo;
	int ret;

	struct rlimit rlim;

	Inicializa_placa();

	// Define tempo máximo que um processo de tempo real pode ocupar o processador
	// Evita que o programa congele o computador
	getrlimit(RLIMIT_RTTIME, &rlim);
	rlim.rlim_cur = 20000000; // 20 segundos
	setrlimit(RLIMIT_RTTIME, &rlim);

	/* Lock memory */
	if (mlockall(MCL_CURRENT | MCL_FUTURE) == -1)
	{
		printf("mlockall failed: %m\n");
		exit(-2);
	}

	/* Initialize pthread attributes (default values) */
	ret = pthread_attr_init(&attr);
	if (ret)
	{
		printf("init pthread attributes failed\n");
		goto out;
	}

	ret = pthread_attr_init(&attr2);
	if (ret)
	{
		printf("init pthread attributes failed\n");
		goto out;
	}

	/* Set a specific stack size  */
	ret = pthread_attr_setstacksize(&attr, PTHREAD_STACK_MIN);
	if (ret)
	{
		printf("pthread setstacksize failed\n");
		goto out;
	}

	ret = pthread_attr_setstacksize(&attr2, PTHREAD_STACK_MIN);
	if (ret)
	{
		printf("pthread setstacksize failed\n");
		goto out;
	}

	/* Use scheduling parameters of attr */
	ret = pthread_attr_setinheritsched(&attr, PTHREAD_EXPLICIT_SCHED);
	if (ret)
	{
		printf("pthread setinheritsched failed\n");
		goto out;
	}
	ret = pthread_attr_setinheritsched(&attr2, PTHREAD_EXPLICIT_SCHED);
	if (ret)
	{
		printf("pthread setinheritsched failed\n");
		goto out;
	}

	/* Set scheduler policy and priority of pthread */
	ret = pthread_attr_setschedpolicy(&attr, SCHED_RR);
	//  ret = pthread_attr_setschedpolicy(&attr, SCHED_OTHER);
	if (ret)
	{
		printf("pthread setschedpolicy failed\n");
		goto out;
	}
	ret = pthread_attr_setschedpolicy(&attr2, SCHED_RR);
	//  ret = pthread_attr_setschedpolicy(&attr, SCHED_OTHER);
	if (ret)
	{
		printf("pthread setschedpolicy failed\n");
		goto out;
	}

	pthread_attr_getschedparam(&attr, &param);
	param.sched_priority = RT_PRIORITY;
	ret = pthread_attr_setschedparam(&attr, &param);
	if (ret)
	{
		printf("pthread setschedparam failed\n");
		goto out;
	}
	param.sched_priority = 1;
	ret = pthread_attr_setschedparam(&attr2, &param);
	if (ret)
	{
		printf("pthread setschedparam failed\n");
		goto out;
	}

	/* Create a pthread with specified attributes */
	ret = pthread_create(&thread, &attr, simple_cyclic_task, NULL);
	//    ret = pthread_create(&thread,NULL, simple_cyclic_task, NULL);  //NO REAL TIME
	if (ret)
	{
		printf("create pthread failed\n");
		goto out;
	}

	ret = pthread_create(&threadProcessamento, &attr2, Thread_Carga_Processamento, NULL);
	if (ret)
	{
		printf("create pthread failed\n");
		goto out;
	}

	ret = pthread_create(&threadArquivo, NULL, Thread_Carga_Arquivo, NULL);
	if (ret)
	{
		printf("create pthread failed\n");
		goto out;
	}

	/* Join the thread and wait until it is done */
	ret = pthread_join(thread, NULL);
	if (ret)
		printf("join pthread failed: %m\n");

	continua = 0;
	/* Join the thread and wait until it is done */
	ret = pthread_join(threadProcessamento, NULL);
	if (ret)
		printf("join pthread failed: %m\n");

	/* Join the thread and wait until it is done */
	ret = pthread_join(threadArquivo, NULL);
	if (ret)
		printf("join pthread failed: %m\n");

	// Stop and clear task
	DAQmxStopTask(AItaskHandle);
	DAQmxClearTask(AItaskHandle);
	DAQmxStopTask(AOtaskHandle);
	DAQmxClearTask(AOtaskHandle);

out:
	return ret;

Error:
	if (DAQmxFailed(error))
		DAQmxGetExtendedErrorInfo(errBuff, 2048);
	if (AItaskHandle != 0)
	{
		DAQmxStopTask(AItaskHandle);
		DAQmxClearTask(AItaskHandle);
	}
	if (DAQmxFailed(error))
		printf("DAQmx Error: %s\n", errBuff);
	return 0;
}
