#include <stdio.h>
#include <string.h>
#include <unity.h>

#include <string>

#include "config.h"
#include "night.h"
#include "report.h"

// docs/serial.md must contain these two lines verbatim (checked below).
static const char* HEADER = "millis,ldr_top,ldr_bottom,ldr_left,ldr_right,pan,tilt,state";
static const char* EXAMPLE = "3600000,512,498,601,587,93,120,tracking";

void setUp() {}
void tearDown() {}

static std::string line(const report::Sample& s, size_t size = report::LINE_SIZE) {
  char buf[report::LINE_SIZE + 16];
  memset(buf, '#', sizeof(buf));
  size_t n = report::format(buf, size, s);
  TEST_ASSERT_EQUAL(strlen(buf), n);
  return std::string(buf);
}

void test_tracking_line() {
  report::Sample s = {3600000UL, {512, 498, 601, 587}, {93, 120}, night::State::Tracking};
  TEST_ASSERT_EQUAL_STRING(EXAMPLE, line(s).c_str());
}

void test_parked_line() {
  report::Sample s = {0, {0, 0, 0, 0}, {0, 90}, night::State::Parked};
  TEST_ASSERT_EQUAL_STRING("0,0,0,0,0,0,90,parked", line(s).c_str());
}

void test_widest_line_fits() {
  report::Sample s = {4294967295UL, {1023, 1023, 1023, 1023}, {180, 165}, night::State::Tracking};
  std::string out = line(s);
  TEST_ASSERT_EQUAL_STRING("4294967295,1023,1023,1023,1023,180,165,tracking", out.c_str());
  TEST_ASSERT_TRUE(out.size() + 1 <= report::LINE_SIZE);
}

void test_line_has_eight_fields_and_no_newline() {
  report::Sample s = {1, {2, 3, 4, 5}, {6, 7}, night::State::Tracking};
  std::string out = line(s);
  int commas = 0;
  for (char c : out) commas += c == ',';
  TEST_ASSERT_EQUAL(7, commas);
  TEST_ASSERT_TRUE(out.find('\n') == std::string::npos);
  TEST_ASSERT_TRUE(out.find('\r') == std::string::npos);
  TEST_ASSERT_TRUE(out.find(' ') == std::string::npos);
}

void test_too_small_buffer_returns_zero_and_empty_string() {
  report::Sample s = {3600000UL, {512, 498, 601, 587}, {93, 120}, night::State::Tracking};
  char buf[10];
  TEST_ASSERT_EQUAL(0, report::format(buf, sizeof(buf), s));
  TEST_ASSERT_EQUAL_STRING("", buf);
  TEST_ASSERT_EQUAL(0, report::format(buf, 0, s));
}

void test_exact_fit_buffer() {
  report::Sample s = {0, {0, 0, 0, 0}, {0, 90}, night::State::Parked};
  const char* expected = "0,0,0,0,0,0,90,parked";
  char buf[32];
  TEST_ASSERT_EQUAL(strlen(expected), report::format(buf, strlen(expected) + 1, s));
  TEST_ASSERT_EQUAL_STRING(expected, buf);
  TEST_ASSERT_EQUAL(0, report::format(buf, strlen(expected), s));
}

void test_serial_settings_match_decisions() {
  TEST_ASSERT_EQUAL(115200UL, config::BAUD);
  TEST_ASSERT_EQUAL(1000UL, config::REPORT_INTERVAL_MS);
}

static bool doc_has_line(const std::string& doc, const char* wanted) {
  size_t start = 0;
  while (start <= doc.size()) {
    size_t end = doc.find('\n', start);
    if (end == std::string::npos) end = doc.size();
    if (doc.compare(start, end - start, wanted) == 0) return true;
    start = end + 1;
  }
  return false;
}

void test_doc_matches_format() {
  FILE* f = fopen(PROJECT_DIR "/docs/serial.md", "r");
  TEST_ASSERT_NOT_NULL_MESSAGE(f, "docs/serial.md missing");
  std::string doc;
  char chunk[256];
  size_t n;
  while ((n = fread(chunk, 1, sizeof(chunk), f)) > 0) doc.append(chunk, n);
  fclose(f);
  TEST_ASSERT_TRUE_MESSAGE(doc_has_line(doc, HEADER), "header line not in docs/serial.md");
  TEST_ASSERT_TRUE_MESSAGE(doc_has_line(doc, EXAMPLE), "example line not in docs/serial.md");
  TEST_ASSERT_TRUE_MESSAGE(doc.find("115200") != std::string::npos, "baud not in doc");
}

int main() {
  UNITY_BEGIN();
  RUN_TEST(test_tracking_line);
  RUN_TEST(test_parked_line);
  RUN_TEST(test_widest_line_fits);
  RUN_TEST(test_line_has_eight_fields_and_no_newline);
  RUN_TEST(test_too_small_buffer_returns_zero_and_empty_string);
  RUN_TEST(test_exact_fit_buffer);
  RUN_TEST(test_serial_settings_match_decisions);
  RUN_TEST(test_doc_matches_format);
  return UNITY_END();
}
