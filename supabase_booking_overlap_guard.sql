CREATE OR REPLACE FUNCTION normalize_booking_room(input_room TEXT)
RETURNS TEXT
LANGUAGE SQL
IMMUTABLE
AS $$
    SELECT CASE UPPER(BTRIM(input_room))
        WHEN 'MEETING ROOM' THEN 'B2036'
        WHEN 'TOEFL TESTING ICT LAB' THEN 'B1037'
        ELSE UPPER(BTRIM(input_room))
    END;
$$;

CREATE OR REPLACE FUNCTION prevent_booking_overlap()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    new_room TEXT;
    new_date DATE;
    new_start TIME;
    new_end TIME;
    conflict_record RECORD;
BEGIN
    new_room := normalize_booking_room(NEW.room);
    new_date := REPLACE(BTRIM(NEW.date), '/', '-')::DATE;
    new_start := BTRIM(NEW.start_time)::TIME;
    new_end := BTRIM(NEW.end_time)::TIME;

    -- Serialize competing writes for the same physical room and date.
    PERFORM pg_advisory_xact_lock(hashtextextended(new_room || '|' || new_date::TEXT, 0));

    IF new_start >= new_end THEN
        RAISE EXCEPTION 'Booking end_time must be after start_time';
    END IF;

    SELECT src, room, date, start_time, end_time
    INTO conflict_record
    FROM (
        SELECT
            'bookings'::TEXT AS src,
            b.room,
            b.date,
            b.start_time,
            b.end_time
        FROM bookings b
        WHERE b.id IS DISTINCT FROM NEW.id
          AND normalize_booking_room(b.room) = new_room
          AND REPLACE(BTRIM(b.date), '/', '-')::DATE = new_date
          AND BTRIM(b.start_time)::TIME < new_end
          AND BTRIM(b.end_time)::TIME > new_start

        UNION ALL

        SELECT
            'room_sessions'::TEXT AS src,
            rs.room,
            rs.date,
            rs.start_time,
            rs.end_time
        FROM room_sessions rs
        WHERE normalize_booking_room(rs.room) = new_room
          AND REPLACE(BTRIM(rs.date), '/', '-')::DATE = new_date
          AND BTRIM(rs.start_time)::TIME < new_end
          AND BTRIM(rs.end_time)::TIME > new_start

        UNION ALL

        SELECT
            'schedule'::TEXT AS src,
            s.room,
            s.date,
            s.start_time,
            s.end_time
        FROM schedule s
        WHERE normalize_booking_room(s.room) = new_room
          AND REPLACE(BTRIM(s.date), '/', '-')::DATE = new_date
          AND BTRIM(s.start_time)::TIME < new_end
          AND BTRIM(s.end_time)::TIME > new_start
    ) conflicts
    LIMIT 1;

    IF FOUND THEN
        RAISE EXCEPTION 'Booking overlaps existing % entry for room % on % at %-%',
            conflict_record.src,
            new_room,
            TO_CHAR(new_date, 'YYYY-MM-DD'),
            conflict_record.start_time,
            conflict_record.end_time;
    END IF;

    NEW.room := new_room;
    NEW.date := TO_CHAR(new_date, 'YYYY/MM/DD');
    NEW.start_time := TO_CHAR(new_start, 'HH24:MI');
    NEW.end_time := TO_CHAR(new_end, 'HH24:MI');
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS bookings_prevent_overlap ON bookings;
CREATE TRIGGER bookings_prevent_overlap
BEFORE INSERT OR UPDATE ON bookings
FOR EACH ROW
EXECUTE FUNCTION prevent_booking_overlap();