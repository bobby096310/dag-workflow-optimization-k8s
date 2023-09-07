import sys
import json

def get_pdf(latency_measures):
    percentages = []
    values = []
    latency_measures.sort()
    min_latency = min(latency_measures)
    max_latency = max(latency_measures)
    start = min_latency
    end = min_latency + 1
    values.append(end)
    count = 0
    index = 0

    while index < len(latency_measures):
        if latency_measures[index] >= start and latency_measures[index] <= end:
            count += 1
            index += 1
        else:
            percentages.append(count / len(latency_measures))
            count = 0
            start += 1
            end += 1
            if (end >= max_latency):
                values.append(max_latency)
            else:
                values.append(end);
    percentages.append(count / len(latency_measures))
    return percentages, values
	
def get_cdf(percentages, values):
        
    # always round the sum of probabilities to 1
    percentages[0] += 1 - sum(percentages)

    out_precentages = []
    out_values = []
    
    percentile = 0
    while (percentile < 100):
        percentile += 5
        out_precentages.append(percentile)
        sum_probabilties = 0
        for i in range(len(values)):

            sum_probabilties += percentages[i]
            if ((sum_probabilties * 100) >= (percentile - 0.0000000001)):
                out_values.append(values[i]);
                break

    return out_precentages, out_values

def get_n(percentage, cdf_perc, cdf_values):
    if (percentage < 0 or percentage > 100):
        return("Invalid percentage range")
        
    else:
        for i in range(len(cdf_perc)):
            if percentage <= cdf_perc[i]:
                return cdf_values[i]
        return("No Result")
        
def get_n_latency(data, n):
    pdf_perc, pdf_values = get_pdf(data)
    cdf_perc, cdf_values = get_cdf(pdf_perc, pdf_values)
    return get_n(n, cdf_perc, cdf_values)

def analyze_result(raw_data, col_index):
    E2Es = []
    for run in raw_data:
        E2Es.append(float(run.split(' ')[col_index]))
    E2E_mean = round(sum(E2Es) / len(E2Es), 2)
    return "Mean " + str(E2E_mean) + " P95 " +  str(get_n_latency(E2Es, 95)) + " Count " + str(len(E2Es))

def main():
    args = sys.argv[1:]
    if(len(args) < 1):
        print("Please enter data")
        return
    data = json.loads(args[0])
    pdf_perc, pdf_values = get_pdf(data)
    print(pdf_perc, pdf_values)
    cdf_perc, cdf_values = get_cdf(pdf_perc, pdf_values)
    print(cdf_perc, cdf_values)
    print(get_n(95, cdf_perc, cdf_values))
    print(get_n_latency(data, 90))
    
    
if __name__ == "__main__":
    main()
