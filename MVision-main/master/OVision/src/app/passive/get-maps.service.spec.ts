import { TestBed } from '@angular/core/testing';

import { GetMapsService } from './get-maps.service';

describe('GetMapsService', () => {
  let service: GetMapsService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(GetMapsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
