#!/bin/bash

show_help() {
    cat << EOF
Usage: $0 -p <provider> [-e <environment>] [-t <test_path>]

Options:
  -p, --provider     Provider to run tests against (required)
  -t, --test-path    Specific test path to run (default: tests/)
  -h, --help         Show this help message

Available providers:
  local-android
  bitbar-android
  local-ios
  sauce-ios
EOF
}

check_env_vars() {
    local missing_vars=""
    
    local provider_vars
    case "$1" in
        "local-android")
            provider_vars="LOCAL_ANDROID_DEVICE_UDID LOCAL_ANDROID_DEVICE_VERSION APPLICATION_LAUNCH_ACTIVITY APPLICATION_PACKAGE"
            ;;
        "bitbar-android") 
            provider_vars="BITBAR_API_KEY BITBAR_APP_ID BITBAR_DEVICE_NAME BITBAR_URL APPLICATION_LAUNCH_ACTIVITY APPLICATION_PACKAGE"
            ;;
        "local-ios")
            provider_vars="LOCAL_IOS_DEVICE_UDID BUNDLE_ID"
            ;;
        "sauce-ios")
            provider_vars="SAUCE_USERNAME SAUCE_ACCESS_KEY SAUCE_DEVICE_NAME SAUCE_PLATFORM_VERSION SAUCE_URL BUNDLE_ID"
            ;;
        *)
            provider_vars=""
            ;;
    esac

    if [ -n "$provider_vars" ]; then
        for var in $provider_vars; do
            eval val="\$${var}"
            if [ -z "$val" ]; then
                missing_vars="$missing_vars $var"
            fi
        done
    fi

    if [ -n "$missing_vars" ]; then
        printf "Error: Missing required environment variables:\n%s\n" "$missing_vars"
        echo "Set variables using: export VARIABLE_NAME=value"
        exit 1
    fi
}

TEST_PATH="tests/"

while getopts ":p:t:h-:" opt; do
    case $opt in
        p) PROVIDER=$OPTARG ;;
        t) TEST_PATH=$OPTARG ;;
        h) show_help; exit 0 ;;
        -)
            case "${OPTARG}" in
                provider) PROVIDER="${!OPTIND}"; OPTIND=$((OPTIND + 1)) ;;
                test-path) TEST_PATH="${!OPTIND}"; OPTIND=$((OPTIND + 1)) ;;
                help) show_help; exit 0 ;;
                *) echo "Unknown option --${OPTARG}"; show_help; exit 1 ;;
            esac
            ;;
        ?) echo "Unknown option -$OPTARG"; show_help; exit 1 ;;
    esac
done

if [[ -z "$PROVIDER" ]]; then
    echo "Error: Provider is required" >&2
    show_help
    exit 1
fi

check_env_vars "$PROVIDER"

BASE_CMD="pytest"

# Use a case statement instead of associative arrays
case "$PROVIDER" in
    "local-android")
        PYTEST_ARGS="
            --provider=local
            --application_type=mobile-native 
            --platform=android
            --device_udid=\"${LOCAL_ANDROID_DEVICE_UDID}\"
            --platform_version=\"${LOCAL_ANDROID_DEVICE_VERSION}\"
            --application_id=\"${APPLICATION_PACKAGE}\"
            --application_launch_activity=\"${APPLICATION_LAUNCH_ACTIVITY}\""
        ;;
    "bitbar-android")
        PYTEST_ARGS="
            --provider=bitbar
            --application_type=mobile-native
            --platform=android 
            --bitbar_project=cw-android
            --bitbar_testrun=\"pytest_run_at_$(date +%Y-%m-%d_%H-%M-%S)\"
            --bitbar_api_key=\"${BITBAR_API_KEY}\"
            --bitbar_app_id=\"${BITBAR_APP_ID}\"
            --device_name=\"${BITBAR_DEVICE_NAME}\"
            --url=\"${BITBAR_URL}\"
            --application_id=\"${APPLICATION_PACKAGE}\"
            --application_launch_activity=\"${APPLICATION_LAUNCH_ACTIVITY}\""
        ;;
    "local-ios")
        PYTEST_ARGS="
            --provider=local
            --application_type=mobile-native
            --platform=ios
            --application_id=\"${BUNDLE_ID}\"
            --device_udid=\"${LOCAL_IOS_DEVICE_UDID}\"
            --platform_version=\"${LOCAL_IOS_DEVICE_VERSION}\""
        ;;
    "sauce-ios")
        PYTEST_ARGS="
            --provider=saucelabs
            --application_type=mobile-native
            --platform=ios
            --application_id=\"${BUNDLE_ID}\"
            --device_name=\"${SAUCE_DEVICE_NAME}\"
            --platform_version=\"${SAUCE_PLATFORM_VERSION}\"
            --url=\"${SAUCE_URL}\"
            --saucelabs_name=\"pytest_run_at_$(date +%Y-%m-%d_%H-%M-%S)\"
            --saucelabs_username=\"${SAUCE_USERNAME}\"
            --saucelabs_access_key=\"${SAUCE_ACCESS_KEY}\""
        ;;
    *)
        echo "Error: Unknown provider '$PROVIDER'"
        show_help
        exit 1
        ;;
esac

PYTEST_ARGS=$(echo "$PYTEST_ARGS" | tr -s ' ' | tr '\n' ' ')
FINAL_CMD="$BASE_CMD $PYTEST_ARGS $ENV_ARGS $TEST_PATH"

printf "Executing:\n%s\n\n" "$FINAL_CMD"

eval "$FINAL_CMD"
