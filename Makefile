# Makefile pentru Tema 3 - Liga Boților

CXX = g++
CXXFLAGS = -Wall -Wextra -std=c++17
TARGET = arena
INPUT = arena.txt
OUTPUT = arena.out

# Găsește automat toate fișierele .cpp din directorul curent
SOURCES = $(wildcard *.cpp)
OBJS = $(SOURCES:.cpp=.o)

.SILENT:

all: test-all

build: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(OBJS)

# Regulă generală pentru compilare .cpp -> .o
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	rm -f *.o $(TARGET) $(OUTPUT) out/*.log out/*.refeed

run: $(TARGET)
	./$(TARGET) < $(INPUT) > $(OUTPUT)

# Teste normale: input precompletat → output
test: $(TARGET)
	@if [ -z "$(TEST)" ]; then \
		echo "❌ Specifică testul: make test TEST=test1"; \
		exit 1; \
	fi
	@mkdir -p out
	@python3 teste/scripturi/verifica.py $(TEST)

# Rulează toate testele
test-all: $(TARGET)
	@mkdir -p out
	@python3 teste/scripturi/verifica.py all
	@if [ -f .test_results.txt ]; then \
		read TRECUTE TOTAL < .test_results.txt; \
		if [ -n "$$SERVER_URL" ]; then \
			python3 teste/scripturi/trimite_rezultate.py $$TRECUTE $$TOTAL "$$SERVER_URL"; \
		elif [ -n "$$SERVER_IP" ]; then \
			python3 teste/scripturi/trimite_rezultate.py $$TRECUTE $$TOTAL "$$SERVER_IP"; \
		fi; \
		rm -f .test_results.txt; \
	fi

# Teste individuale (test1, test2, ..., test20)
test1 test2 test3 test4 test5 test6 test7 test8 test9 test10 \
test11 test12 test13 test14 test15 test16 test17 test18 test19 test20: $(TARGET)
	@mkdir -p out
	@python3 teste/scripturi/verifica.py $@

# Salvează transcriptul pentru duel (transformă output în format REF)
record: $(TARGET)
	@if [ -z "$(TEST)" ]; then \
		echo "❌ Specifică testul: make record TEST=test1"; \
		exit 1; \
	fi
	@mkdir -p out
	@python3 teste/scripturi/verifica.py $(TEST)
	@echo "✅ Log salvat în teste/output/$(TEST).out"

# Duel între două executabile (pentru bonus)
# Folosește: make duel STUDENT_A=./arena_studentA STUDENT_B=./arena_studentB TEST=test01
duel: 
	@if [ -z "$(STUDENT_A)" ] || [ -z "$(STUDENT_B)" ] || [ -z "$(TEST)" ]; then \
		echo "❌ Folosește: make duel STUDENT_A=./arena1 STUDENT_B=./arena2 TEST=test01"; \
		exit 1; \
	fi
	@mkdir -p out
	@echo "⚔️  Pornesc duelul între $(STUDENT_A) și $(STUDENT_B) pe $(TEST)..."
	@python3 teste/scripturi/run_duel.sh $(STUDENT_A) $(STUDENT_B) $(TEST) || true
	@echo "✅ Duel terminat. Verifică out/duel_$(TEST)_*.log"

# Duel live cu named pipe (timp real)
duel-live:
	@if [ -z "$(STUDENT_A)" ] || [ -z "$(STUDENT_B)" ] || [ -z "$(TEST)" ]; then \
		echo "❌ Folosește: make duel-live STUDENT_A=./arena1 STUDENT_B=./arena2 TEST=test01"; \
		exit 1; \
	fi
	@mkdir -p out
	@mkfifo /tmp/arena_duel_pipe 2>/dev/null || true
	@echo "⚔️  Duel live între $(STUDENT_A) și $(STUDENT_B)..."
	@timeout 60 bash -c '$(STUDENT_A) < teste/input/$(TEST).in | tee out/studentA_$(TEST).log | $(STUDENT_B) > out/studentB_$(TEST).log' || true
	@rm -f /tmp/arena_duel_pipe
	@echo "✅ Duel terminat. Verifică out/studentA_$(TEST).log și out/studentB_$(TEST).log"

# Duel cu output → input (output student A devine input pentru student B)
duel-turnbased:
	@if [ -z "$(STUDENT_A)" ] || [ -z "$(STUDENT_B)" ] || [ -z "$(TEST)" ]; then \
		echo "❌ Folosește: make duel-turnbased STUDENT_A=./arena1 STUDENT_B=./arena2 TEST=test01"; \
		exit 1; \
	fi
	@mkdir -p out
	@echo "⚔️  Duel turn-based: $(STUDENT_A) → $(STUDENT_B)..."
	@# Runde 1: Student A primește input inițial
	@$(STUDENT_A) < teste/input/$(TEST).in > out/round1_A.out
	@# Transformă output-ul lui A în format REF pentru B
	@python3 teste/scripturi/oficializeaza_transcriere.py out/round1_A.out > out/round1_A.refeed
	@# Runde 2: Student B primește output-ul lui A
	@$(STUDENT_B) < out/round1_A.refeed > out/round2_B.out
	@# Transformă output-ul lui B în format REF pentru A
	@python3 teste/scripturi/oficializeaza_transcriere.py out/round2_B.out > out/round2_B.refeed
	@# Runde 3: Student A primește output-ul lui B (continuă până la SCOREBOARD)
	@$(STUDENT_A) < out/round2_B.refeed > out/round3_A.out || true
	@echo "✅ Duel turn-based terminat. Verifică out/round*_*.out"

verify: $(TARGET)
	./$(TARGET) < $(INPUT) > $(OUTPUT)
	@echo "✅ Verifică manual $(OUTPUT)"

key:
	@if [ -f "teste/scripturi/key.txt" ] && [ -s "teste/scripturi/key.txt" ]; then \
		echo "✓ Cheia există deja în teste/scripturi/key.txt"; \
		echo "🔑 Cheia ta: $$(cat teste/scripturi/key.txt)"; \
		echo ""; \
		echo "Folosește această cheie pentru a edita nickname-ul pe rezultate.eu/tema3"; \
	else \
		KEY=$$(python3 -c "import uuid; print(uuid.uuid4().hex)"); \
		echo "$$KEY" > teste/scripturi/key.txt; \
		echo "════════════════════════════════════════════════════════════"; \
		echo "✓ Cheie unică generată și salvată în teste/scripturi/key.txt"; \
		echo "════════════════════════════════════════════════════════════"; \
		echo ""; \
		echo "🔑 Cheia ta: $$KEY"; \
		echo ""; \
		echo "📌 PAȘI URMĂTORI:"; \
		echo "   1. git add teste/scripturi/key.txt"; \
		echo "   2. git commit -m \"Add personal key\""; \
		echo "   3. git push"; \
		echo "   4. Accesează rezultate.eu/tema3 și editează nickname-ul"; \
		echo ""; \
		echo "⚠️  IMPORTANT: Salvează această cheie! O vei folosi pentru"; \
		echo "    a edita nickname-ul pe https://rezultate.eu/tema3"; \
		echo ""; \
		echo "════════════════════════════════════════════════════════════"; \
		echo ""; \
	fi

.PHONY: all clean run test test-all test01 test02 test03 test04 test05 test06 test07 test08 test09 test10 \
	test11 test12 test13 test14 test15 test16 test17 test18 test19 test20 record duel duel-live duel-turnbased verify key

