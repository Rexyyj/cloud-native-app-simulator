/*
Copyright 2023 Telefonaktiebolaget LM Ericsson AB

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

	http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

package generate

import (
	"application-generator/src/pkg/model"
	"fmt"

	"k8s.io/apimachinery/pkg/util/validation"
)

// Occurrences returns the number of occurrences of every value in a slice of strings
func Occurrences(strSlice []string) map[string]int {
	occurrences := make(map[string]int)
	for _, entry := range strSlice {
		occurrences[entry]++
	}
	return occurrences
}

func ValidateNames(config *model.FileConfig) error {
	serviceNames := []string{}

	// Validate service names (RFC 1035 DNS Label)
	for _, service := range config.Services {
		errs := validation.IsDNS1035Label(service.Name)

		// There can be several conformance errors but only one is returned by this function
		// If the user fixes one error, the next error will be shown when running the generator again
		if len(errs) > 0 {
			return fmt.Errorf("Service '%s' has invalid name: %s", service.Name, errs[0])
		}

		serviceNames = append(serviceNames, service.Name)
	}

	serviceNameOccurences := Occurrences(serviceNames)

	for _, service := range config.Services {
		// Duplicate name found
		if serviceNameOccurences[service.Name] > 1 {
			return fmt.Errorf("Duplicate service name '%s'", service.Name)
		}

		endpointNames := []string{}

		// Validate endpoint names (RFC 1123 DNS Subdomain)
		for _, endpoint := range service.Endpoints {
			errs := validation.IsDNS1123Subdomain(endpoint.Name)

			if len(errs) > 0 {
				return fmt.Errorf("Endpoint '%s' has invalid name: %s", endpoint.Name, errs[0])
			}

			endpointNames = append(endpointNames, endpoint.Name)
		}

		endpointNameOccurences := Occurrences(serviceNames)

		for _, endpoint := range service.Endpoints {
			// Duplicate name found
			if endpointNameOccurences[endpoint.Name] > 1 {
				return fmt.Errorf("Duplicate endpoint '%s' in service '%s'", endpoint.Name, service.Name)
			}
		}
	}

	return nil
}

// Validates an input JSON config provided by the user
func ValidateFileConfig(config *model.FileConfig) error {
	if err := ValidateNames(config); err != nil {
		return err
	}

	return nil
}
